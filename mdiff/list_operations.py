from typing import Union


def move_list_elements(l: list, src_i: Union[int, slice], tgt_i: int):
    if isinstance(src_i, int):
        src_i = slice(src_i, src_i + 1)
    if src_i.stop <= src_i.start:
        return
    if src_i.step is not None and src_i.step > 1:
        raise ValueError('Invalid slice object passed. Only continuous sequences can be moved')

    seq = l[src_i]

    del l[src_i]
    if tgt_i > src_i.start:
        tgt_i -= len(seq)

    l[tgt_i:tgt_i] = seq


l = list(range(10))
move_list_elements(l, slice(7, 10), 0)
