import math
from typing import NamedTuple, Union


class OpCode(NamedTuple):
    tag: str
    i1: int
    i2: int
    j1: int
    j2: int


def longest_increasing_subsequence(x, key=lambda x: x, a_lt_b=lambda a, b: a < b):
    """
    Returns:
        Sequence of tuples (i, v), where:
            i - index of element in sequence
            v - value of element in sequence
    """
    # source https://en.wikipedia.org/wiki/Longest_increasing_subsequence
    n = len(x)
    p = [0] * n
    m = [0] * (n + 1)
    l = 0

    for i in range(n):
        # Binary search for the largest positive j ≤ L such that X[M[j]] < X[i]
        lo = 1
        hi = l + 1
        while lo < hi:
            mid = lo + math.floor((hi - lo) / 2)
            if a_lt_b(key(x[m[mid]]), key(x[i])):
                lo = mid + 1
            else:
                hi = mid

        # After searching, lo is 1 greater than the length of the longest prefix of X[i]
        new_l = lo

        # The predecessor of X[i] is the last index of the subsequence of length new_l-1
        p[i] = m[new_l - 1]
        m[new_l] = i

        if new_l > l:
            # If we found a subsequence longer than any we've found yet, update L
            l = new_l

    # Reconstruct the longest increasing subsequence
    s = [0] * l
    indexes = []
    k = m[l]
    for i in reversed(range(l)):
        s[i] = k, x[k]
        k = p[k]

    return s


def move_list_elements(l: list, src_i: Union[int, slice], tgt_i: int):
    # l = list(range(10))
    # move_list_elements(l,2,5)
    # # move_list_elements(l, slice(7, 10), 0)
    # # move_list_elements(l, slice(1, 4), 5)
    # xx = 1
    if isinstance(src_i, int):
        src_i = slice(src_i, src_i + 1)
    if src_i.stop <= src_i.start:
        return
    if src_i.step is not None and src_i.step > 1:
        raise ValueError('Invalid slice object passed. Only continuous sequences can be moved')

    seq = l[src_i]

    del l[src_i]
    if tgt_i > src_i.start:
        # tgt_i -= len(seq)
        pass

    l[tgt_i:tgt_i] = seq