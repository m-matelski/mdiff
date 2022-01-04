from collections import namedtuple
from dataclasses import dataclass, field
from itertools import chain
from operator import attrgetter
from typing import Any, List, Tuple, Union, Dict, Sequence

from mdiff.block_move import Block, find_block_moves
from mdiff.list_operations import move_list_elements


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


@dataclass
class OpCode:
    tag: str
    i1: int
    i2: int
    j1: int
    j2: int


@dataclass
class MoveBlock:
    """
    Stores information about detected subsequence to move in diff algorithm.
        i: start position of move subsequence in OA table.
        n: first value of move subsequence in OA table (used to detect blocks offset).
        w: length of subsequence (weight).
    """
    i: int
    n: int
    w: int


class HeckelDiff:
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
        for i in reversed(range(len(na))):
            try:
                if isinstance(na[i], int):
                    j = na[i]
                    if isinstance(na[i - 1], SymbolTableEntry) and na[i - 1] == oa[j - 1]:
                        oa[j - 1] = i - 1
                        na[i - 1] = j - 1
            except IndexError:
                pass

        # pass 5.5
        for idx, i in enumerate(na):
            if isinstance(i, SymbolTableEntry):
                i.olno = idx

        self.st = st
        self.na = na
        self.oa = oa

    @staticmethod
    def is_valid_symbol_table_move_entry(e: SymbolTableEntryType) -> bool:
        """Checks if algorithm's symbol table record is a move operation"""
        return isinstance(e, int) and e >= 0

    @staticmethod
    def is_valid_symbol_table_unique_entry(e: SymbolTableEntryType) -> bool:
        return isinstance(e, SymbolTableEntry)

    @staticmethod
    def _generate_move_blocks(a: List[SymbolTableEntryType]) -> Sequence[MoveBlock]:
        """
        Generates move blocks data from algorithm result.
        Returns Tuples of (move block start index, move block first element value (int), length of move block)
        Data in that format will be used to find least moves needed to create target sequence.
        """
        prev = None
        block_start_n = block_start_idx = block_len = 0
        in_block = False
        for idx, i in enumerate(a):
            # close block
            if in_block and (not HeckelDiff.is_valid_symbol_table_move_entry(i) or (
                    HeckelDiff.is_valid_symbol_table_move_entry(prev) and i != prev + 1) or i == -1):
                yield MoveBlock(i=block_start_idx, n=block_start_n, w=block_len)
                in_block = False
            # open block
            if not in_block and HeckelDiff.is_valid_symbol_table_move_entry(i):
                block_start_n = i
                block_start_idx = idx
                block_len = 0
                in_block = True
            prev = i
            block_len += 1
        # last block
        if in_block:
            yield MoveBlock(i=block_start_idx, n=block_start_n, w=block_len)

    @staticmethod
    def _generate_insert_delete_block(a: List[SymbolTableEntryType]) -> Sequence[MoveBlock]:
        prev = None
        block_start_n = block_start_idx = block_len = 0
        in_block = False
        for idx, i in enumerate(a):
            # close block
            if not HeckelDiff.is_valid_symbol_table_unique_entry(i) and in_block:
                yield MoveBlock(i=block_start_idx, n=block_start_n, w=block_len)
                in_block = False
            # open block
            if not in_block and HeckelDiff.is_valid_symbol_table_unique_entry(i):
                block_start_n = i
                block_start_idx = idx
                block_len = 0
                in_block = True
            prev = i
            block_len += 1
        # last block
        if in_block:
            yield MoveBlock(i=block_start_idx, n=block_start_n, w=block_len)

    def generate_move_blocks(self):
        yield from HeckelDiff._generate_move_blocks(self.na)

    def generate_move_and_equal_opcodes(self) -> Sequence[OpCode]:
        mb = list(self.generate_move_blocks())
        blocks_p = [Block(mb.n, mb.w) for mb in mb]
        block_moves = list(find_block_moves(blocks_p))
        for i, b in enumerate(mb):
            # move
            if i in block_moves:
                yield OpCode('move', b.i, b.i + b.w, b.n, b.n) # Target shoudl be empty slice? or + w
                yield OpCode('moved', b.i, b.i, b.n, b.n + b.w)
            else:
                yield OpCode('equal', b.i, b.i + b.w, b.n, b.n + b.w)  # Target shoudl be empty slice? or + w

    def generate_insert_blocks(self):
        yield from HeckelDiff._generate_insert_delete_block(self.oa)

    def generate_insert_opcodes(self):
        bb = list(self.generate_insert_blocks())
        for b in self.generate_insert_blocks():
            yield OpCode('insert', b.n.olno, b.n.olno, b.i, b.i + b.w)
            # yield OpCode('insert', b.i, b.i, b.i, b.i + b.w)

    def generate_delete_opcodes(self):
        bb = list(self.generate_delete_blocks())
        for b in self.generate_delete_blocks():
            # TODO: olno is always 0 for delete? Does it have ny meaning position in target?
            yield OpCode('delete', b.i, b.i + b.w, b.n.olno, b.n.olno)

    def generate_delete_blocks(self):
        yield from HeckelDiff._generate_insert_delete_block(self.na)

    def get_opcodes(self):
        self.alg()
        opcodes = list(chain(self.generate_move_and_equal_opcodes(), self.generate_insert_opcodes(), self.generate_delete_opcodes()))

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

        # sort it
        result = []
        ipos = 0
        jpos = 0
        finished = False

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

        return result





a = ['F3', 'F5', 'F1', 'F2', 'F7']
b = ['F1', 'F4', 'F6', 'F2', 'F3', 'F8']

# a = ['F1', 'F2', 'F3']
# b = ['F1', 'F3', 'F2']

a = ["MUCH", "WRITING", "IS", "LIKE", "SNOW", ",",
     "A", "MASS", "OF", "LONG", "WORDS", "AND",
     "PHRASES", "FALLS", "UPON", "THE", "RELEVANT",
     "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]
b = ["A", "MASS", "OF", "LATIN", "WORDS", "FALLS",
     "UPON", "THE", "RELEVANT", "FACTS", "LIKE", "SOFT",
     "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

# Common only
# old
# a = ["LIKE", "SNOW", ",",
#      "A", "MASS", "OF", "WORDS",
#      "FALLS", "UPON", "THE", "RELEVANT",
#      "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]
#
# # new
# b = ["A", "MASS", "OF", "WORDS", "FALLS",
#      "UPON", "THE", "RELEVANT", "FACTS", "LIKE",
#      "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

# et answer = vec![Delete(0), Delete(1), Delete(2), Delete(9),
#                   Delete(11), Delete(12), Move(6, 0), Move(7, 1),
#                   Move(8, 2), Create(3), Move(10, 4), Move(13, 5),
#                   Move(14, 6), Move(15, 7), Move(16, 8), Move(17, 9),
#                   Move(3, 10), Create(11), Move(4, 12), Move(5, 13)];


# hd = HeckelDiff(a, b)
# hd.alg()

# hd_blocks1 = list(HeckelDiff.generate_move_blocks([1, 2, 3, 's', 7, 8, 's', 5]))

# hd.get_opcodes()
xxx = 1
