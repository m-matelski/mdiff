from dataclasses import dataclass


@dataclass
class SymbolTableEntry:
    oc: int = 0
    nc: int = 0
    olno: int = 0


def iso_diff_rs(o, n):
    # symbol table, NA array, OA array
    st = dict()
    na = [None for i in range(len(n))]
    oa = [None for i in range(len(o))]

    # pass 1
    for x in n:
        ste = st.setdefault(x, SymbolTableEntry())
        ste.nc += 1

    # pass 2
    for i, x in enumerate(o):
        ste = st.setdefault(x, SymbolTableEntry())
        ste.oc += 1
        ste.olno = i

    # pass 3
    for i in range(len(na)):
        tx = st[n[i]]
        if tx.nc == tx.oc == 1:
            na[i] = tx.olno
            oa[tx.olno] = i

    # pass4
    for i in range(len(na)):
        try:
            j = na[i]
            if na[i + 1] is None and oa[j + 1] is None and n[i + 1] == o[j + 1]:
                oa[j + 1] = i + 1
                na[i + 1] = j + 1
        except (IndexError, TypeError):
            pass

    # pass 5
    for i in reversed(range(len(na))):
        try:
            j = na[i]
            if na[i - 1] is None and oa[j - 1] is None and n[i - 1] == o[j - 1]:
                oa[j - 1] = i - 1
                na[i - 1] = j - 1
        except (IndexError, TypeError):
            pass

    # pass 6
    result = []
    delete_offsets = []  # initialized?
    offset = 0
    for i, x in enumerate(oa):
        delete_offsets.append(offset)
        if x is None:
            result.append(('delete', i))
            offset += 1

    offset = 0
    for i, x in enumerate(na):
        if x is not None:
            try:
                j = x
                if o[j] != n[i]:
                    result.append(('update', i))
                if j + offset - delete_offsets[i] != i:
                    result.append(('move', (j, i)))
            except (IndexError, TypeError):
                pass
        else:
            result.append(('create', i, j))
            offset += 1

    return result


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

# et answer = vec![Delete(0), Delete(1), Delete(2), Delete(9),
#                   Delete(11), Delete(12), Move(6, 0), Move(7, 1),
#                   Move(8, 2), Create(3), Move(10, 4), Move(13, 5),
#                   Move(14, 6), Move(15, 7), Move(16, 8), Move(17, 9),
#                   Move(3, 10), Create(11), Move(4, 12), Move(5, 13)];


# [('delete', 0), ('delete', 1), ('delete', 2), ('delete', 9), ('delete', 11), ('delete', 12), ('move', (6, 0)),
#  ('update', 1), ('move', (6, 1)), ('update', 2), ('move', (6, 2)), ('create', 3), ('update', 4), ('update', 5),
#  ('move', (6, 5)), ('update', 6), ('move', (6, 6)), ('update', 7), ('move', (6, 7)), ('update', 8), ('move', (6, 8)),
#  ('update', 9), ('move', (6, 9)), ('update', 10), ('move', (6, 10)), ('create', 11), ('update', 12), ('move', (6, 12)),
#  ('update', 13), ('move', (6, 13)), ('update', 14), ('move', (6, 14)), ('update', 15), ('move', (6, 15)),
#  ('update', 16), ('move', (6, 16)), ('update', 17), ('move', (6, 17)), ('update', 18), ('move', (6, 18))]

r2 = iso_diff_rs(a, b)

xxx = 1
