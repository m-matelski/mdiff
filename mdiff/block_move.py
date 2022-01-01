from collections import namedtuple
from typing import List, Tuple

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
