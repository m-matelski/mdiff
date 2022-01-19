from dataclasses import dataclass
from typing import Any, List, Union, Dict, Sequence, NamedTuple


from mdiff.block_extractor import HeckelSequenceNonUniqueEntriesBlockExtractor, ConsecutiveVectorBlockExtractor
from mdiff.utils import OpCode, longest_increasing_subsequence


@dataclass
class SymbolTableEntry:
    """
    Heckel's diff algorithm symbol table entry.
    """
    value: Any
    oc: int = 0
    nc: int = 0
    olno: int = 0


SymbolTableEntryType = Union[int, SymbolTableEntry]


class MoveBlock(NamedTuple):
    """
    Stores information about detected subsequence to move in diff algorithm.
        i: start position of move subsequence in OA table.
        n: first value of move subsequence in OA table (used to detect blocks offset).
        w: length of subsequence (weight).
    """
    i: int
    n: SymbolTableEntryType
    w: int


class HeckelSequenceMatcher:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.st: Dict[Any, SymbolTableEntryType] = dict()
        self.na: List[SymbolTableEntryType] = list()
        self.oa: List[SymbolTableEntryType] = list()

    def alg(self):
        # symbol table, NA array, OA array
        st: Dict[Any, SymbolTableEntryType] = dict()
        na: List[SymbolTableEntryType] = list()
        oa: List[SymbolTableEntryType] = list()

        for idx, i in enumerate(self.a):
            ste = st.setdefault(i, SymbolTableEntry(i))
            ste.nc += 1
            na.append(ste)

        for idx, i in enumerate(self.b):
            ste = st.setdefault(i, SymbolTableEntry(i))
            ste.oc += 1
            oa.append(ste)
            ste.olno = idx

        # pass3
        for i in range(len(na)):
            if na[i].nc == na[i].oc == 1:
                olno = na[i].olno
                na[i] = olno
                oa[olno] = i

        # pass4
        for i in range(len(na)):
            try:
                if isinstance(na[i], int):
                    j = na[i]
                    if isinstance(na[i + 1], SymbolTableEntry) and na[i + 1] == oa[j + 1]:
                        oa[j + 1] = i + 1
                        na[i + 1] = j + 1
            except IndexError:
                pass

        # pass5
        for i in reversed(range(1, len(na))):
            try:
                if isinstance(na[i], int):
                    j = na[i]
                    if isinstance(na[i - 1], SymbolTableEntry) and na[i - 1] == oa[j - 1] and i >= 1 and j >= 1:
                        oa[j - 1] = i - 1
                        na[i - 1] = j - 1
            except IndexError:
                pass

        # pass 5.5
        for idx, i in enumerate(na):
            if isinstance(i, SymbolTableEntry):
                # mark deletes source indexes
                i.olno = idx

        self.st = st
        self.na = na
        self.oa = oa

    def generate_move_and_equal_opcodes(self) -> Sequence[OpCode]:
        # New order of sequence elements that exists in both sequences is stored in NA table after algorithm run.
        # Integer type entries in NA indicates that element of sequence might be either equal or moved.
        # Extract from NA tables only move/equal entries.
        # Index is added because NA integer entries will be converted to consecutive entries blocks.
        # Block will have form of tuple = (block_start_index, block_start_value, block_length) corresponding to NA table
        # NA table can consist of SymbolTableEntry type rows which breaks the block.
        # Adding enumerate index allow to detect block break caused by SymbolTableEntry type record.
        na_indexed_moves = [(idx, i) for idx, i in enumerate(self.na) if isinstance(i, int)]

        # Longest increasing sequence finds "equal" entries.
        # Indexed NA in form of tuples are used in order to use index to build proper MoveBlocks later.
        lis = longest_increasing_subsequence(na_indexed_moves, key=lambda x: x[1])
        lis_idx, lis_v = zip(*lis) if lis else ([], [])

        # Finding consecutive vector blocks and mapping them to NA indexes and starting values.
        cons_all_blocks = list(ConsecutiveVectorBlockExtractor(na_indexed_moves).extract_blocks())
        all_blocks = [MoveBlock(i=na_indexed_moves[i][0], n=na_indexed_moves[i][1], w=w) for i, w in cons_all_blocks]

        # Finding consecutive vector blocks in LIS and mapping them to NA indexes and starting values.
        cons_eq_blocks = list(ConsecutiveVectorBlockExtractor(lis_v).extract_blocks())
        eq_blocks = [MoveBlock(i=lis_v[i][0], n=lis_v[i][1], w=w) for i, w in cons_eq_blocks]

        # The difference of all NA blocks and "equal" blocks found by LIS, gives list of optimal move operation blocks.
        move_blocks = set(all_blocks) - set(eq_blocks)

        # Yield OpCodes
        for b in eq_blocks:
            yield OpCode('equal', b.i, b.i + b.w, b.n, b.n + b.w)

        for b in move_blocks:
            yield OpCode('move', b.i, b.i + b.w, b.n, b.n)
            yield OpCode('moved', b.i, b.i, b.n, b.n + b.w)

    def generate_insert_opcodes(self):
        block_extractor = HeckelSequenceNonUniqueEntriesBlockExtractor(self.oa)
        insert_blocks = [MoveBlock(i, self.oa[i], w) for i, w in block_extractor.extract_blocks()]
        for b in insert_blocks:
            yield OpCode('insert', b.n.olno, b.n.olno, b.i, b.i + b.w)

    def generate_delete_opcodes(self):
        block_extractor = HeckelSequenceNonUniqueEntriesBlockExtractor(self.na)
        delete_blocks = [MoveBlock(i, self.na[i], w) for i, w in block_extractor.extract_blocks()]
        for b in delete_blocks:
            yield OpCode('delete', b.i, b.i + b.w, b.n.olno, b.n.olno)

    def get_opcodes(self):
        self.alg()

        insert_opcodes = list(self.generate_insert_opcodes())
        delete_opcodes = list(self.generate_delete_opcodes())
        move_opcodes = []
        moved_opcodes = []
        equal_opcodes = []
        map_dict = {
            'move': move_opcodes,
            'moved': moved_opcodes,
            'equal': equal_opcodes
        }
        for opcode in self.generate_move_and_equal_opcodes():
            map_dict[opcode.tag].append(opcode)

        # opcodes should be already sorted
        moved_opcodes.sort(key=lambda x: x.j1)
        move_opcodes.sort(key=lambda x: x.i1)

        # sort it
        result = []
        ipos = 0
        jpos = 0

        while True:
            if len(delete_opcodes) > 0 and delete_opcodes[0].i1 == ipos:
                opcode = delete_opcodes.pop(0)
                result.append(opcode)
                ipos = opcode.i2
                continue

            if len(move_opcodes) > 0 and move_opcodes[0].i1 == ipos:
                opcode = move_opcodes.pop(0)
                result.append(opcode)
                ipos = opcode.i2
                continue

            if len(equal_opcodes) > 0 and equal_opcodes[0].i1 == ipos and equal_opcodes[0].j1 == jpos:
                opcode = equal_opcodes.pop(0)
                result.append(opcode)
                ipos = opcode.i2
                jpos = opcode.j2
                continue

            if len(insert_opcodes) > 0 and insert_opcodes[0].j1 == jpos:
                opcode = insert_opcodes.pop(0)
                result.append(opcode)
                jpos = opcode.j2
                continue

            if len(moved_opcodes) > 0 and moved_opcodes[0].j1 == jpos:
                opcode = moved_opcodes.pop(0)
                result.append(opcode)
                jpos = opcode.j2
                continue

            break

        # TODO Fold delete -> insert into replace
        # be = HeckelDeleteThenInsertBlockExtractor(result)
        # b = list(be.extract_blocks())
        # for i in b:
        #     delete = result[i[0]]
        #     insert = result[i[0]+1]
        #     replace = OpCode('replace', delete.i1, delete.i2, insert.j1, insert.j2)
        #     result[i[0]: i[0]+2] = [replace]
        #     x = 1

        return result

