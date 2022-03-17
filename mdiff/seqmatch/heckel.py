from collections import deque
from dataclasses import dataclass, field
from typing import Any, List, Union, Dict, Sequence, NamedTuple

from mdiff.block_extractor import NonIntegersBlockExtractor, ConsecutiveVectorBlockExtractor, \
    OpCodeDeleteThenInsertBlockExtractor
from mdiff.utils import OpCode, longest_increasing_subsequence, get_idx_or_default


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

    def get_opcodes2(self) -> List[OpCode]:
        """Fast opcodes"""
        self._alg()

        # heckel info:
        # 1. If na[j] points to table_entry - insert
        # 2. if na[j] points to oa[i], but na[j+1] dont point to oa[i+1], j is boundary of deletion, or block move

        # 1. iterate through oa and na at the same time using oa[i] na[j] indexes
        # 2. if oa[j] is int, and na[i] is table_entry - start delete block, i++
        # 3. if oa[j] is table_entry, and na[i] is int - start insert block, j++
        # 3.5 eventually if 2. oa[j] is table_entry and na[i] is table entry - start replace block, i++ j++
        # 4. if oa[j] is int, and na[i] is int:
        #   a. if oa[j] == i and na[i] == j - start equal block, i++ j++
        #   b. else if i <= oa[j] then move block i++, else i > oa[j] then moved block j++
        opcodes = []
        i = j = 0
        na = lambda x: get_idx_or_default(self.na, x, None)
        oa = lambda x: get_idx_or_default(self.oa, x, None)



        while i < len(self.na) or j < len(self.oa):
            # if not curr_tag:
            prev_i = i
            prev_j = j

            while isinstance(na(i), HeckelSymbolTableEntry):
                i += 1
            delete_opcode = OpCode('delete', prev_i, i, j, j) if i > prev_i else None

            while isinstance(oa(j), HeckelSymbolTableEntry):
                j += 1
            insert_opcode = OpCode('insert', i, i, prev_j, j) if j > prev_j else None

            if delete_opcode and insert_opcode and self.replace_mode:
                rep_opcode = OpCode('replace', delete_opcode.i1, delete_opcode.i2, insert_opcode.j1, insert_opcode.j2)
                opcodes.append(rep_opcode)
                continue
            elif delete_opcode and insert_opcode and not self.replace_mode:
                opcodes.append(delete_opcode)
                opcodes.append(insert_opcode)
                continue
            elif delete_opcode:
                opcodes.append(delete_opcode)
                continue
            elif insert_opcode:
                opcodes.append(insert_opcode)
                continue

            if isinstance(na(i), int) and isinstance(oa(j), int):
                while na(i) == j and oa(j) == i:
                    i += 1
                    j += 1
                if i > prev_i:
                    opcodes.append(OpCode('equal', prev_i, i, prev_j, j))
                    continue

                while na(i) != j and i <= oa(j):
                    i += 1
                if i > prev_i:
                    opcodes.append(OpCode('move', prev_i, i, j, j))
                    continue

                while na(i) != j and i > oa(j):
                    j += 1
                if j > prev_j:
                    opcodes.append(OpCode('moved', i, i, prev_j, j))
                    continue

        return opcodes

    def get_opcodes(self) -> List[OpCode]:
        self._alg()

        # heckel info:
        # 1. If na[j] points to table_entry - insert
        # 2. if na[j] points to oa[i], but na[j+1] dont point to oa[i+1], j is boundary of deletion, or block move

        # 1. iterate through oa and na at the same time using oa[i] na[j] indexes
        # 2. if oa[j] is int, and na[i] is table_entry - start delete block, i++
        # 3. if oa[j] is table_entry, and na[i] is int - start insert block, j++
        # 3.5 eventually if 2. oa[j] is table_entry and na[i] is table entry - start replace block, i++ j++
        # 4. if oa[j] is int, and na[i] is int:
        #   a. if oa[j] == i and na[i] == j - start equal block, i++ j++
        #   b. else if i <= oa[j] then move block i++, else i > oa[j] then moved block j++
        opcodes = []
        i = j = 0
        na = lambda x: get_idx_or_default(self.na, x, None)
        oa = lambda x: get_idx_or_default(self.oa, x, None)

        na_indexed_moves = [(idx, i) for idx, i in enumerate(self.na) if isinstance(i, int)]
        # Longest increasing sequence finds "equal" entries.
        # Indexed NA in form of tuples are used in order to use index to build proper MoveBlocks later.
        lis = deque(longest_increasing_subsequence(na_indexed_moves, key=lambda x: x[1]))
        lis_idx, lis_v = zip(*lis) if lis else ([], [])
        x = 1

        while i < len(self.na) or j < len(self.oa):
            # if not curr_tag:
            prev_i = i
            prev_j = j

            while isinstance(na(i), HeckelSymbolTableEntry):
                i += 1
            delete_opcode = OpCode('delete', prev_i, i, j, j) if i > prev_i else None

            while isinstance(oa(j), HeckelSymbolTableEntry):
                j += 1
            insert_opcode = OpCode('insert', i, i, prev_j, j) if j > prev_j else None

            if delete_opcode and insert_opcode and self.replace_mode:
                rep_opcode = OpCode('replace', delete_opcode.i1, delete_opcode.i2, insert_opcode.j1, insert_opcode.j2)
                opcodes.append(rep_opcode)
                continue
            elif delete_opcode and insert_opcode and not self.replace_mode:
                opcodes.append(delete_opcode)
                opcodes.append(insert_opcode)
                continue
            elif delete_opcode:
                opcodes.append(delete_opcode)
                continue
            elif insert_opcode:
                opcodes.append(insert_opcode)
                continue

            if isinstance(na(i), int) and isinstance(oa(j), int):
                while lis and i == lis[0][1][0] and j == lis[0][1][1]:
                    i += 1
                    j += 1
                    lis.popleft()
                if i > prev_i:
                    opcodes.append(OpCode('equal', prev_i, i, prev_j, j))
                    continue

                while not lis or i != lis[0][1][0]:
                    i += 1
                    if lis:
                        lis.popleft()
                if i > prev_i:
                    opcodes.append(OpCode('move', prev_i, i, j, j))
                    continue

                while not lis or j != lis[0][1][1]:
                    j += 1
                    if lis:
                        lis.popleft()
                if j > prev_j:
                    opcodes.append(OpCode('moved', i, i, prev_j, j))
                    continue

        return opcodes


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
