"""
This module provides functions and structures for common package usage.
"""

import math
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Any, Tuple, List, Sequence, Union, Protocol, Type


class OpCode:
    """
    Data object for storing sequences differences opcodes in a python built-in difflib manner.
        tag: sequence operation i.e: 'insert', 'delete', 'equal', 'move', 'moved'.
        i1: source sequence start of tagged difference.
        i2: source sequence end of tagged difference.
        j1: target sequence start of tagged difference.
        j2: target sequence end of tagged difference.
    """
    __tuple_attribs = ('tag', 'i1', 'i2', 'j1', 'j2')

    def __init__(self, tag, i1, i2, j1, j2):
        self.tag = tag
        self.i1 = i1
        self.i2 = i2
        self.j1 = j1
        self.j2 = j2

    def __get_tuple_attributes(self):
        return tuple(self.__dict__[attrib] for attrib in self.__tuple_attribs)

    def __iter__(self):
        return iter(self.__get_tuple_attributes())

    def __getitem__(self, item):
        if isinstance(item, slice):
            return tuple(self.__dict__[key] for key in self.__tuple_attribs[item])
        return self.__dict__[self.__tuple_attribs[item]]

    def __eq__(self, other):
        return self.__get_tuple_attributes() == other.__get_tuple_attributes()

    def __repr__(self):
        return f'{self.__class__.__name__}{self.__get_tuple_attributes()}'

    def __str__(self):
        return repr(self)


OpCodeType = Union[OpCode, Tuple[str, int, int, int, int]]
OpCodesType = Sequence[OpCodeType]


class SequenceMatcherBase(Protocol):
    def get_opcodes(self) -> List[OpCodeType]:
        ...

    def set_seqs(self, a, b):
        ...

    def set_seq1(self, a):
        ...

    def set_seq2(self, b):
        ...


class CompositeOpCode(OpCode):
    def __init__(self, tag, i1, i2, j1, j2):
        super().__init__(tag, i1, i2, j1, j2)
        self.children_opcodes: List[OpCode] = []

    def __repr__(self):
        return f"{super().__repr__()}{'*' if self.children_opcodes else ''}"


def longest_increasing_subsequence(x: Sequence[Any], key=lambda x: x, a_lt_b=lambda a, b: a < b) \
        -> List[Tuple[int, Any]]:
    """
    Function returns longest increasing subsequence of sequence x.
    It is slightly modified version of algorithm from: https://en.wikipedia.org/wiki/Longest_increasing_subsequence.

    Parameters:
        x:
            Input sequence
        key:
            Function that extracts attributes from elements to compare - by default compares elements by itself.
        a_lt_b:
            Function that compares that element 'a' of a sequence is less than element 'b'.
            Returns simple a < b comparison result by default.

    Returns:
        s:
            Subsequence in a form of List of tuples (i, v), where:
            i - index of element in sequence
            v - value of element in sequence

    Examples:
    >>> longest_increasing_subsequence([1, 2, 7, 8, 3, 4])
    [(0, 1), (1, 2), (4, 3), (5, 4)]

    >>> longest_increasing_subsequence([(4, 2), (5, 3), (6, 1)], key=lambda t: t[1])
    [(0, (4, 2)), (1, (5, 3))]

    >>> longest_increasing_subsequence([1, 2, 7, 8, 3, 4], a_lt_b=lambda a, b: a > b)
    [(3, 8), (5, 4)]
    """
    n = len(x)
    p = [0] * n
    m = [0] * (n + 1)
    g = 0

    for i in range(n):
        # Binary search for the largest positive j ≤ L such that X[M[j]] < X[i]
        lo = 1
        hi = g + 1
        while lo < hi:
            mid = lo + math.floor((hi - lo) / 2)
            if a_lt_b(key(x[m[mid]]), key(x[i])):
                lo = mid + 1
            else:
                hi = mid

        # After searching, lo is 1 greater than the length of the longest prefix of X[i]
        new_g = lo

        # The predecessor of X[i] is the last index of the subsequence of length new_l-1
        p[i] = m[new_g - 1]
        m[new_g] = i

        if new_g > g:
            # If we found a subsequence longer than any we've found yet, update L
            g = new_g

    # Reconstruct the longest increasing subsequence
    s = [0] * g
    k = m[g]
    for i in reversed(range(g)):
        s[i] = k, x[k]
        k = p[k]

    return s


def sequences_equal(a: Sequence[Any], b: Sequence[Any]) -> bool:
    """Compares sequences elements and returns True if they are all equal."""
    return tuple(a) == tuple(b)


def move_list_elements(lst: list, src_i: Union[int, slice], tgt_i: int):
    """
    Move elements in list "lst" from index/slice "src_i" to "tgt_i" position.
    If tgt_i is out of list boundary it moves elements to the list edge.

    Parameters:
        lst: list reference to move elements.
        src_i: source list index or slice. Only slice with step=1.
        tgt_i: target list index.

    Examples:
        >>> l = [0, 1, 2, 3, 4, 5]
        >>> move_list_elements(l, 2, 4)
        >>> l
        [0, 1, 3, 4, 2, 5]

        >>> l = [0, 1, 2, 3, 4, 5]
        >>> move_list_elements(l, 4, 2)
        >>> l
        [0, 1, 4, 2, 3, 5]

        >>> l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> move_list_elements(l, slice(2, 5), 6)
        >>> l
        [0, 1, 5, 6, 7, 8, 2, 3, 4, 9]

        >>> l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> move_list_elements(l, slice(2, 5), 999)
        >>> l
        [0, 1, 5, 6, 7, 8, 9, 2, 3, 4]

        >>> l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> move_list_elements(l, slice(2, 5), -2)
        >>> l
        [0, 1, 5, 6, 7, 2, 3, 4, 8, 9]

    """
    if isinstance(src_i, int):
        src_i = slice(src_i, src_i + 1)
    if src_i.stop <= src_i.start:
        return
    if src_i.step is not None and src_i.step > 1:
        raise ValueError('Invalid slice object passed. Only continuous sequences can be moved')

    seq = lst[src_i]

    del lst[src_i]
    if tgt_i > src_i.start:
        pass

    lst[tgt_i:tgt_i] = seq


def len_or_1(a):
    """
    Returns len(a) if a is Iterable. Returns 1 otherwise.
    """
    try:
        return len(a)
    except TypeError:
        return 1


def read_file(p: Path):
    with open(p) as file:
        content = file.read()
    return content


class AttributeSequenceHandler:
    def __init__(self, seq):
        self.seq = seq

    def __call__(self, *args, **kwargs):
        return [i(*args, **kwargs) for i in self.seq]


class CompositeDelegationMixin:
    """
    This class provides auto delegation super class methods to children instances.
    It allows to treat composite object as single instance, also direct inheritance allows IDE to generate hints.
    """

    def __init__(self):
        self.__children__ = []

    def __getattribute__(self, item):
        # Do not delegate, until children defined (avoids error when instance uses self in init process)
        try:
            children = object.__getattribute__(self, '__children__')
        except AttributeError:
            children = []
        if not children:
            return object.__getattribute__(self, item)

        if item == '__children__':
            return object.__getattribute__(self, item)
        children_items = [object.__getattribute__(i, item) for i in self.__children__]
        if callable(object.__getattribute__(self, item)):
            # Assumption: if base class attribute is callable, then all that children attributes are callable
            return AttributeSequenceHandler(children_items)
        else:
            return children_items


class StringEnumChoice(str, Enum):
    """
    Base class for typer choice enum strings. Predefined __str__ method fixes the bug where
    default showed StringEnumChoice.value instead of value
    """

    def __str__(self):
        return self.value


def get_enum_values(enum: Type[Enum]):
    return [e.value for e in enum]


def pop_default(lst: List, index=-1, default=None):
    try:
        return lst.pop(index)
    except IndexError:
        return default


def sort_seq_by_other_seq_indexes(seq: Sequence, other: Sequence) -> List[Tuple[int, Any]]:
    b_hash = dict()
    seq = enumerate(seq)
    for i, item in enumerate(other):
        b_hash.setdefault(item, []).append(i)

    result = sorted(seq, key=lambda x: pop_default(b_hash.get(x[1], []), 0, math.inf))
    return result


def sort_seq_by_other_seq(seq: Sequence, other: Sequence) -> List:
    return [i[1] for i in sort_seq_by_other_seq_indexes(seq, other)]


def sort_string_seq_by_other(seq: Sequence[str], other: Sequence[str], case_sensitive=True) -> List[str]:
    if case_sensitive:
        a_seq = seq
        b_seq = other
    else:
        a_seq = [i.lower() for i in seq]
        b_seq = [i.lower() for i in other]

    idx_sort, _ = zip(*sort_seq_by_other_seq_indexes(a_seq, b_seq))
    result = [seq[i] for i in idx_sort]
    return result


def sort_string_seq(seq: Sequence[str], case_sensitive=True) -> List[str]:
    if case_sensitive:
        return sorted(seq)
    else:
        return sorted(seq, key=lambda x: x.lower())


@lru_cache
def get_app_version() -> str:
    version = read_file(Path('../VERSION'))
    return version
