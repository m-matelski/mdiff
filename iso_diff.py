from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any, List, Tuple

Block = namedtuple('Block', 'n w')


def any_move_set_brut_force(blocks: List[Block], blocks_used: Tuple[bool], fav: str = 'blocks_weight'):
    available_blocks = [b for i, b in enumerate(blocks) if not blocks_used[i]]

    if available_blocks:
        prev_n = available_blocks[0].n
    else:
        return []
    ordered = True
    best_result = []
    best_result_weight_sum = 0

    for i, b in enumerate(blocks):
        if blocks_used[i]:
            continue

        # checking the order of n members in list of Blocks, if ordered - end recursion at the end
        if b.n < prev_n:
            ordered = False
        prev_n = b.n

        # branch recursion with available blocks
        # mark current block as used ...
        updated_block_used = list(blocks_used)
        updated_block_used[i] = True
        updated_block_used = tuple(updated_block_used)
        # ... and pass it to next recursion level
        current_result = [i] + any_move_set_brut_force(blocks, updated_block_used)

        if fav == 'blocks_number':
            # best result for smallest number of operations
            if not best_result or len(current_result) < len(best_result):
                best_result = current_result
        elif fav == 'blocks_weight':
            # best result for smallest weight of operation
            current_result_weight_sum = sum(blocks[i].w for i in current_result)
            if not best_result or current_result_weight_sum < best_result_weight_sum:
                best_result = current_result
                best_result_weight_sum = current_result_weight_sum
        else:
            best_result = current_result

    if ordered:
        return []
    else:
        return best_result


def _find_block_moves_rec(blocks: List[Block], blocks_used: Tuple[bool], memo: dict, fav: str = 'blocks_weight'):
    if blocks_used in memo:
        return memo[blocks_used]

    available_blocks = [b for i, b in enumerate(blocks) if not blocks_used[i]]

    if available_blocks:
        prev_n = available_blocks[0].n
    else:
        return []
    ordered = True
    best_result = []
    best_result_weight_sum = 0

    for i, b in enumerate(blocks):
        if blocks_used[i]:
            continue

        # checking the order of n members in list of Blocks, if ordered - end recursion at the end
        if b.n < prev_n:
            ordered = False
        prev_n = b.n

        # branch recursion with available blocks
        # mark current block as used ...
        updated_block_used = list(blocks_used)
        updated_block_used[i] = True
        updated_block_used = tuple(updated_block_used)
        # ... and pass it to next recursion level
        current_result = [i] + _find_block_moves_rec(blocks, updated_block_used, memo, fav)
        memo[updated_block_used] = current_result

        if fav == 'blocks_number':
            # best result for smallest number of operations
            if not best_result or len(current_result) < len(best_result):
                best_result = current_result
        elif fav == 'blocks_weight':
            # best result for smallest weight of operation
            current_result_weight_sum = sum(blocks[i].w for i in current_result)
            if not best_result or current_result_weight_sum < best_result_weight_sum:
                best_result = current_result
                best_result_weight_sum = current_result_weight_sum
        else:
            best_result = current_result

    if ordered:
        return []
    else:
        return best_result


def find_block_moves(blocks: List[Block], fav: str = 'blocks_weight'):
    blocks_used = tuple([False] * len(blocks))
    memo = dict()
    return _find_block_moves_rec(blocks, blocks_used, memo, fav)


def find_block_moves_dynamic(blocks: List[Block], fav: str = 'blocks_weight'):
    blocks_used = [0] * len(blocks)
    tab = list(range(len(blocks)))
    tab[0] = blocks_used

    for cur_blocks_used in tab:
        best_result = []
        for i, b in enumerate(cur_blocks_used):
            if not b:
                new_blocks_used = cur_blocks_used.copy()
                new_blocks_used[i] = True


blocks1 = [Block(2, 3), Block(1, 2), Block(0, 4)]
blocks2 = [Block(0, 2), Block(1, 1), Block(2, 0)]
blocks3 = [Block(2, 2), Block(1, 4), Block(4, 2), Block(0, 5), Block(3, 3)]
blocks4 = [Block(0, 7), Block(2, 2), Block(3, 2), Block(4, 2), Block(1, 7)]

r1 = any_move_set_brut_force(blocks1, tuple([False] * len(blocks1)))
r2 = any_move_set_brut_force(blocks2, tuple([False] * len(blocks2)))
r3 = any_move_set_brut_force(blocks3, tuple([False] * len(blocks3)))

#
rn1 = find_block_moves(blocks1)
rn2 = find_block_moves(blocks2)
rn3 = find_block_moves(blocks3)
rn4_w = find_block_moves(blocks4, fav='blocks_weight')
rn4_n = find_block_moves(blocks4, fav='blocks_number')

xxx = 1



def many(a: int):
    return True if a > 1 else False


@dataclass
class SymbolTableEntry:
    key: Any
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
        ste = st.setdefault(i, SymbolTableEntry(i))
        ste.nc += 1
        na.append(ste)

    for idx, i in enumerate(o):
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

# a = ["MUCH", "WRITING", "IS", "LIKE", "SNOW", ",",
#      "A", "MASS", "OF", "LONG", "WORDS", "AND",
#      "PHRASES", "FALLS", "UPON", "THE", "RELEVANT",
#      "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]
# b = ["A", "MASS", "OF", "LATIN", "WORDS", "FALLS",
#      "UPON", "THE", "RELEVANT", "FACTS", "LIKE", "SOFT",
#      "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]



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


r1 = iso_diff(a, b)

xxx = 1
