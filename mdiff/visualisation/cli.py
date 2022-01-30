from itertools import zip_longest
from typing import Sequence, Union, Tuple

from colorama import Fore, init, Back, Style

from mdiff.utils import OpCode, len_or_1

init(autoreset=True)

OpCodes = Union[Sequence[OpCode], Sequence[Tuple[str, int, int, int, int]]]


def print_opcodes(a: Sequence, b: Sequence, opcodes: OpCodes):
    for tag, i1, i2, j1, j2 in opcodes:
        print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))


def simple_seq_comparison(a: Sequence, b: Sequence, opcodes: OpCodes):
    a_longest = max([len_or_1(i) for i in a])
    b_longest = max([len_or_1(i) for i in b])
    left_col_len = a_longest + 3
    right_col_len = b_longest + 3

    colormode = Fore

    print_format = f'{{left_op:1}} {{left_f:<{left_col_len}}} || {{right_op:1}} {{right_f:<{right_col_len}}}'
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            for left, right in zip(a[i1:i2], b[j1:j2]):
                print(print_format.format(left_op='', left_f=left, right_op='', right_f=right))
        if tag == 'insert':
            for right in b[j1:j2]:
                print(colormode.GREEN + print_format.format(left_op='', left_f='', right_op='+', right_f=right))
        if tag == 'delete':
            for left in a[i1:i2]:
                print(colormode.RED + print_format.format(left_op='-', left_f=left, right_op='', right_f=''))
        if tag == 'replace':
            for left, right in zip_longest(a[i1:i2], b[j1:j2], fillvalue=''):
                print(colormode.YELLOW + print_format.format(left_op='R', left_f=left, right_op='R', right_f=right))
        if tag == 'move':
            for left in a[i1:i2]:
                print(colormode.BLUE + print_format.format(left_op='M', left_f=left, right_op='', right_f=''))
        if tag == 'moved':
            for right in b[j1:j2]:
                print(colormode.BLUE + print_format.format(left_op='', left_f='', right_op='M', right_f=right))
