from dataclasses import dataclass, field


def many(a: int):
    return True if a > 1 else False


@dataclass
class SymbolTableEntry:
    oc: int = 0
    nc: int = 0
    olno: int = 0


# a, b are sequences to compare (e.g. list of text lines)
def iso_diff(o, n):
    # symbol table, NA array, OA array
    st = dict()
    na = list()
    oa = list()

    for idx, i in enumerate(n):
        ste = st.setdefault(i, SymbolTableEntry())
        ste.nc += 1
        na.append(ste)

    for idx, i in enumerate(o):
        ste = st.setdefault(i, SymbolTableEntry())
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

    # An array na now contains information needed
    # to list (or encode) the differences:
    # - if na[i] points to a symbol table entry - insert (new text)
    # - if na[i] points to oa[j] but na[j+1] doesn't point to oa[j+1]
    #   then line i is at the boundary of deletion or block move

    x = 1
    return na



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

# et answer = vec![Delete(0), Delete(1), Delete(2), Delete(9),
#                   Delete(11), Delete(12), Move(6, 0), Move(7, 1),
#                   Move(8, 2), Create(3), Move(10, 4), Move(13, 5),
#                   Move(14, 6), Move(15, 7), Move(16, 8), Move(17, 9),
#                   Move(3, 10), Create(11), Move(4, 12), Move(5, 13)];


r1 = iso_diff(a, b)

xxx = 1
