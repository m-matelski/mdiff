# a covering set of T with respect to S, is set of block moves (p,q,l) such as
# every symbol T[i] appears in S is included in exactly one block move (one character is used in one block move)
# minimal covering set is smallest covering set
def minimal_covering_set(s, t):
    q = 0
    m = len(s)
    n = len(t)
    result = []
    while q < n:
        l = p = p_cur = 0
        while p_cur + 1 < m and q + 1 < n:
            l_cur = 0
            while p_cur + l_cur < m and q + l_cur < n and s[p_cur+l_cur] == t[q+l_cur]:
                l_cur += 1
            # minimal size of blocks to move ? breaks the algoritm picking the last, not the biggest
            if l_cur >= 1:
                l = l_cur
                p = p_cur
            p_cur += 1
        if l>0:
            result.append((p,q,l))
        q += max(1, l)
    return result


def minimal_covering_set(s, t):
    q = 0
    m = len(s)
    n = len(t)
    result = []
    while q < n:
        l = p = p_cur = 0
        while p_cur + 1 < m and q + 1 < n:
            l_cur = 0
            while p_cur + l_cur < m and q + l_cur < n and s[p_cur+l_cur] == t[q+l_cur]:
                l_cur += 1
            # minimal size of blocks to move ? breaks the algoritm picking the last, not the biggest
            if l_cur >= 1:
                l = l_cur
                p = p_cur
            p_cur += 1
        if l>0:
            result.append((p,q,l))
        q += max(1, l)
    return result

a = 'uvwuvwxy'
b = 'zuvwxwu'

# a = '35127'
# b = '146238'

# a = ['F3', 'F5', 'F1', 'F2', 'F7']
# b = ['F1', 'F4', 'F6', 'F2', 'F3', 'F8']

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

res = minimal_covering_set(a, b)
xxxx = 1