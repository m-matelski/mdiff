from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, List


@dataclass
class Entry:
    value: Any
    src_indexes: List[int] = field(default_factory=list)
    tgt_indexes: List[int] = field(default_factory=list)
    curr_src_idx: int = 0
    curr_tgt_idx: int = 0


# s and t are hashable sequences
def comp(s, t):
    tab = dict()

    for i, x in enumerate(s):
        e = tab.setdefault(x, Entry(value=x))
        e.src_indexes.append(i)

    for i, x in enumerate(t):
        e = tab.setdefault(x, Entry(value=x))
        e.tgt_indexes.append(i)

    offset = 0
    src_idx = tgt_idx = 0
    while src_idx < len(s) and tgt_idx < len(t):
        sl = s[src_idx]
        tl = t[tgt_idx]
        se = tab[sl]
        te = tab[tl]

    # The longest common subsequence in Python

# Function to find lcs_algo
def lcs_algo(S1, S2):
    m = len(S1)
    n = len(S2)
    L = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # Building the mtrix in bottom-up way
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif S1[i - 1] == S2[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    index = L[m][n]

    lcs_res = [""] * (index + 1)
    lcs_res[index] = ""

    i = m
    j = n
    while i > 0 and j > 0:

        if S1[i - 1] == S2[j - 1]:
            lcs_res[index - 1] = S1[i - 1]
            i -= 1
            j -= 1
            index -= 1

        elif L[i - 1][j] > L[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return lcs_res

# S1 = "ACADB"
# S2 = "CBDA"
# m = len(S1)
# n = len(S2)
# lcs_algo(S1, S2)
#




a = ['F3', 'F5', 'F1', 'F2', 'F7']
b = ['F1', 'F4', 'F6', 'F2', 'F3', 'F8']

# a = ['F1', 'F2', 'F3']
# b = ['F1', 'F3', 'F2']

# old
# a = ["MUCH", "WRITING", "IS", "LIKE", "SNOW", ",",
#      "A", "MASS", "OF", "LONG", "WORDS", "AND",
#      "PHRASES", "FALLS", "UPON", "THE", "RELEVANT",
#      "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]
#
# # new
# b = ["A", "MASS", "OF", "LATIN", "WORDS", "FALLS",
#      "UPON", "THE", "RELEVANT", "FACTS", "LIKE", "SOFT",
#      "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

sm = SequenceMatcher(None, a, b)
lon_block = sm.find_longest_match()
blocks = sm.get_matching_blocks()
lcs2= [a[block.a:(block.a + block.size)] for block in sm.get_matching_blocks()]



lcs = lcs_algo(a, b)
res = comp(a, b)
a = 1
xxx=1
x= 1
