from dataclasses import dataclass, field
from typing import Any, List, Union, Dict, Sequence, NamedTuple

from mdiff.block_extractor import NonIntegersBlockExtractor, ConsecutiveVectorBlockExtractor, \
    OpCodeDeleteThenInsertBlockExtractor
from mdiff.utils import OpCode, longest_increasing_subsequence


@dataclass
class HeckelSymbolTableEntry:
    """
    Heckel's diff algorithm symbol table entry.
    """
    value: Any
    oc: int = 0
    nc: int = 0
    olno: int = 0


HeckelSymbolTableEntryType = Union[int, HeckelSymbolTableEntry]


class HeckelSequenceMatcherException(Exception):
    pass


class OpBlock(NamedTuple):
    """
    Stores information about detected subsequence operation block in diff algorithm.
        i: start position of subsequence in OA table.
        n: first value of subsequence in OA table (used to detect blocks offset).
        w: length of subsequence (weight).
    """
    i: int
    n: HeckelSymbolTableEntryType
    w: int


def _map_replace_opcodes(opcodes: Sequence[OpCode]):
    """
    This method takes sequence of OpCodes as an input, and merges consecutive pairs of "insert" and "delete"
    blocks into "replace" operation.
    """
    replace_blocks = list(OpCodeDeleteThenInsertBlockExtractor(opcodes).extract_blocks())
    replace_block_idx = 0
    replace_result = []
    i = 0
    while i < len(opcodes):
        # check if replace block
        if replace_block_idx < len(replace_blocks) and replace_blocks[replace_block_idx][0] == i:
            rep_block = replace_blocks[replace_block_idx]
            delete = opcodes[rep_block[0]]
            insert = opcodes[rep_block[0] + 1]
            replace = OpCode('replace', delete.i1, delete.i2, insert.j1, insert.j2)
            replace_result.append(replace)
            replace_block_idx += 1
            i += 2
        else:
            replace_result.append(opcodes[i])
            i += 1
    return replace_result


class HeckelSequenceMatcher:
    """
    HeckelSequenceMatcher is a class for comparing pairs of sequences of any type, as long as sequences
    are comparable and hashable. Unlike builtin difflib.SequenceMatcher, it detects and marks elements
    displacement between sequences. This class provides get_opcodes() method which returns Sequence of opcodes
    with differences between sequences in a similar manner as difflib.SequenceMatcher.get_opcodes() does, but
    with additional "move" and "moved" tags for displaced elements.

    Unlike difflib.SequenceMatcher - this class doesn't provide any additional functionality for generating
    human-readable sequence comparisons.

    Parameters:
        a:
            source(old) sequence.
        b:
            target(new) sequence.
        replace_mode:
            if True: it merges consecutive pairs of "insert" and "delete" blocks into "replace" operation.
            Remains "insert" and "delete" blocks otherwise.

    HeckelSequenceMatcher uses implementation of Paul Heckel's algorithm described in
    "A Technique for Isolating Differences Between Files" paper, which can be found here:
    http://documents.scribd.com/docs/10ro9oowpo1h81pgh1as.pdf
    """

    def __init__(self, a: Sequence[Any] = '', b: Sequence[Any] = '', replace_mode=True):
        self.a = a
        self.b = b
        self.replace_mode = replace_mode
        self.st: Dict[Any, HeckelSymbolTableEntryType] = {}
        self.na: List[HeckelSymbolTableEntryType] = []
        self.oa: List[HeckelSymbolTableEntryType] = []

    def set_seq1(self, a):
        self.a = a

    def set_seq2(self, b):
        self.b = b

    def set_seqs(self, a, b):
        self.set_seq1(a)
        self.set_seq2(b)

    def _alg(self):
        """
        Implementation of Paul Heckel's algorithm described in "A Technique for Isolating Differences Between Files".
        """
        # symbol table, NA array, OA array
        st: Dict[Any, HeckelSymbolTableEntryType] = dict()
        na: List[HeckelSymbolTableEntryType] = list()
        oa: List[HeckelSymbolTableEntryType] = list()

        # pass 1
        for idx, i in enumerate(self.a):
            ste = st.setdefault(i, HeckelSymbolTableEntry(i))
            ste.nc += 1
            na.append(ste)

        # pass 2
        for idx, i in enumerate(self.b):
            ste = st.setdefault(i, HeckelSymbolTableEntry(i))
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
                    if isinstance(na[i + 1], HeckelSymbolTableEntry) and na[i + 1] == oa[j + 1]:
                        oa[j + 1] = i + 1
                        na[i + 1] = j + 1
            except IndexError:
                pass

        # pass5
        for i in reversed(range(1, len(na))):
            try:
                if isinstance(na[i], int):
                    j = na[i]
                    if isinstance(na[i - 1], HeckelSymbolTableEntry) and na[i - 1] == oa[j - 1] and i >= 1 and j >= 1:
                        oa[j - 1] = i - 1
                        na[i - 1] = j - 1
            except IndexError:
                pass

        self.st = st
        self.na = na
        self.oa = oa

    def _generate_move_and_equal_opcodes(self) -> Sequence[OpCode]:
        """
        Generates sequence of OpCode tuples where tags are in: "equal", "move", "moved".
        """
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
        all_blocks = [OpBlock(i=na_indexed_moves[i][0], n=na_indexed_moves[i][1], w=w) for i, w in cons_all_blocks]

        # Finding consecutive vector blocks in LIS and mapping them to NA indexes and starting values.
        cons_eq_blocks = list(ConsecutiveVectorBlockExtractor(lis_v).extract_blocks())
        eq_blocks = [OpBlock(i=lis_v[i][0], n=lis_v[i][1], w=w) for i, w in cons_eq_blocks]

        # The difference of all NA blocks and "equal" blocks found by LIS, gives list of optimal move operation blocks.
        move_blocks = set(all_blocks) - set(eq_blocks)

        # Yield OpCodes
        for b in eq_blocks:
            yield OpCode('equal', b.i, b.i + b.w, b.n, b.n + b.w)

        for b in move_blocks:
            yield OpCode('move', b.i, b.i + b.w, b.n, b.n)
            yield OpCode('moved', b.i, b.i, b.n, b.n + b.w)

    def _generate_insert_opcodes(self):
        """
        Generates sequence of OpCode tuples with tag "insert".
        """
        block_extractor = NonIntegersBlockExtractor(self.oa)
        insert_blocks = [OpBlock(i, self.oa[i], w) for i, w in block_extractor.extract_blocks()]
        for b in insert_blocks:
            yield OpCode('insert', b.n.olno, b.n.olno, b.i, b.i + b.w)

    def _generate_delete_opcodes(self):
        """
        Generates sequence of OpCode tuples with tag "delete".
        """
        block_extractor = NonIntegersBlockExtractor(self.na)
        delete_blocks = [OpBlock(i, self.na[i], w) for i, w in block_extractor.extract_blocks()]
        for b in delete_blocks:
            yield OpCode('delete', b.i, b.i + b.w, b.n.olno, b.n.olno)

    def get_opcodes(self) -> List[OpCode]:
        """
        Returns list of OpCode objects describing how to turn sequence "a" into "b".
        OpCode consists of attributes: tag, i1, i2, j1, j2. OpCode can be unpacked as tuple
        (to be consistent with difflib.SequenceMatcher.get_opcodes() result)

        Usually the first tuple has i1 == j1 == 0, and remaining tuples have i1 equal to the i2
        from the preceding tuple, and, likewise, j1 equal to the previous j2. However this rule is broken when
        "move" and "moved" tags appears in OpCodes list, due to sequence elements displacement detection.

        The tags are strings, with these meanings:
            'replace':  a[i1:i2] should be replaced by b[j1:j2]
            'delete':   a[i1:i2] should be deleted. Note that j1==j2 in this case.
            'insert':   b[j1:j2] should be inserted at a[i1:i1]. Note that i1==i2 in this case.
            'equal':    a[i1:i2] == b[j1:j2]
            'move':     a[i1:i2] should be moved to b[j1:j2] position. Note that j1==j2 in this case.
            'moved':    is opposite tag for 'move'. It's not an operation necessary for turning sequence "a" into "b".
                        It indicates that b[j1:j2] is moved from i1 position
                        (or b[j1:j2] should be moved back to a[i1:i2]). Note that i1==j2 in this case.
                        It can be used for sequence elements movement visualisation.
        """

        self._alg()
        # Prepare opcodes
        insert_opcodes = list(self._generate_insert_opcodes())
        delete_opcodes = list(self._generate_delete_opcodes())
        move_opcodes = []
        moved_opcodes = []
        equal_opcodes = []
        map_dict = {
            'move': move_opcodes,
            'moved': moved_opcodes,
            'equal': equal_opcodes
        }
        for opcode in self._generate_move_and_equal_opcodes():
            map_dict[opcode.tag].append(opcode)

        # sort opcodes (insert, delete and equal opcodes are already sorted)
        moved_opcodes.sort(key=lambda x: x.j1)
        move_opcodes.sort(key=lambda x: x.i1)

        # Fetch opcodes in correct order
        result = []
        ipos = 0
        jpos = 0
        while any([insert_opcodes, delete_opcodes, move_opcodes, moved_opcodes, equal_opcodes]):
            if len(delete_opcodes) > 0 and delete_opcodes[0].i1 == ipos:
                opcode = delete_opcodes.pop(0)
                # j1 and j2 attributes are meaningless for delete operation. However replacing them with jpos
                # keep j-indexes in sync with j-indexes in other returned tags, like in builtin difflib library.
                result.append(OpCode(opcode.tag, opcode.i1, opcode.i2, jpos, jpos))
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
                # i1 and i2 attributes are meaningless for insert operation. However replacing them with ipos
                # keep i-indexes in sync with i-indexes in other returned tags, like in builtin difflib library.
                result.append(OpCode(opcode.tag, ipos, ipos, opcode.j1, opcode.j2))
                jpos = opcode.j2
                continue

            if len(moved_opcodes) > 0 and moved_opcodes[0].j1 == jpos:
                opcode = moved_opcodes.pop(0)
                result.append(opcode)
                jpos = opcode.j2
                continue

            raise HeckelSequenceMatcherException('Invalid indexes in generated OpCodes. Something went wrong.')

        if self.replace_mode:
            result = _map_replace_opcodes(result)

        return result


# ------------------------------------------------------------------------------------
# ----------------------- DisplacementSequenceMatcher --------------------------------
# ------------------------------------------------------------------------------------
@dataclass
class DisplacementMatcherEntry:
    """
    DisplacementSequenceMatcher's algorithm symbol table entry.
        key_val: sequence element value
        a_indexes: key_val appearance indexes in sequence "a".
        b_indexes: key_val appearance indexes in sequence "b".
        a_curr_idx: current a_indexes position.
        b_curr_idx: current b_indexes position.
    """
    key_val: Any
    a_indexes: List[int] = field(default_factory=lambda: [])
    b_indexes: List[int] = field(default_factory=lambda: [])
    a_curr_idx: int = 0
    b_curr_idx: int = 0


class DisplacementSequenceMatcher(HeckelSequenceMatcher):
    """
    DisplacementSequenceMatcher is a variation of HeckelSequenceMatcher class.
    Unlike HeckelSequenceMatcher, the algorithm keeps tracking of every sequence element occurrence, which might give
    better result when both sequences have many common duplicated elements. It tries to detect all sequences elements
    displacements, where HeckelSequenceMatcher might sometimes treat displaced elements as delete/insert.
    Use this class if finding all sequences displacements is crucial.

    Parameters:
        a:
            source(old) sequence.
        b:
            target(new) sequence.
        replace_mode:
            if True: it merges consecutive pairs of "insert" and "delete" blocks into "replace" operation.
            Remains "insert" and "delete" blocks otherwise.
    """

    def __init__(self, a='', b='', replace_mode=True):
        """
        Overridden init from HeckelSequenceMatcher class.
        """
        super().__init__(a, b, replace_mode)
        self.st: Dict[Any, DisplacementMatcherEntry] = {}
        self.na = []
        self.oa = []

    def setup(self):
        self.st = {}
        self.na = []
        self.oa = []

    def add_entries(self):
        """
        Fills algorithm's symbol table.
        """
        for idx, i in enumerate(self.a):
            e = self.st.setdefault(i, DisplacementMatcherEntry(key_val=i))
            e.a_indexes.append(idx)

        for idx, i in enumerate(self.b):
            e = self.st.setdefault(i, DisplacementMatcherEntry(key_val=i))
            e.b_indexes.append(idx)

    def _alg(self):
        """
        Overridden algorithm.
        """
        self.setup()
        self.add_entries()

        for idx, i in enumerate(self.a):
            try:
                e = self.st[i].b_indexes[self.st[i].b_curr_idx]
                self.st[i].b_curr_idx += 1
            except IndexError:
                # table entry values don't have much meanings
                e = HeckelSymbolTableEntry(i, 0, 0, idx)
            self.na.append(e)

        for idx, i in enumerate(self.b):
            try:
                e = self.st[i].a_indexes[self.st[i].a_curr_idx]
                self.st[i].a_curr_idx += 1
            except IndexError:
                # table entry values don't have much meanings
                e = HeckelSymbolTableEntry(i, 0, 0, idx)
            self.oa.append(e)
