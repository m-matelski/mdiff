import abc
from dataclasses import dataclass
from itertools import zip_longest
from math import log10
from operator import itemgetter
from typing import Sequence, Dict, Literal, Union, Tuple

import colorama

from mdiff.utils import CompositeOpCode, OpCodeType, OpCode

STYLE_RESET = colorama.Style.RESET_ALL + colorama.Fore.RESET + colorama.Back.RESET


@dataclass
class ConsoleCharacters:
    sep_line_num: str
    symbol_line_equal: str
    symbol_line_delete: str
    symbol_line_insert: str
    symbol_line_move: str
    symbol_line_move_up: str
    symbol_line_move_down: str
    symbol_line_replace: str
    symbol_line_similar: str
    line_fill_char: str

    def __post_init__(self):
        self.op_char = {
            'equal': self.symbol_line_equal,
            'delete': self.symbol_line_delete,
            'insert': self.symbol_line_insert,
            'move': self.symbol_line_move,
            'moved': self.symbol_line_move,
            'replace': self.symbol_line_replace
        }

    def get_op_char(self, tag: str):
        return self.op_char[tag]


@dataclass
class ConsoleColors:
    line_delete: str
    line_insert: str
    line_move: str
    line_replace: str
    line_equal: str
    line_filler: str
    in_line_equal: str
    in_line_delete: str
    in_line_insert: str
    in_line_move: str
    in_line_replace: str
    label_equal: str
    label_delete: str
    label_insert: str
    label_move: str
    label_replace: str

    def __post_init__(self):
        self.line = {
            'delete': self.line_delete,
            'insert': self.line_insert,
            'move': self.line_move,
            'replace': self.line_replace,
            'equal': self.line_equal,
            'moved': self.line_move
        }

        self.in_line = {
            'equal': self.in_line_equal,
            'delete': self.in_line_delete,
            'insert': self.in_line_insert,
            'move': self.in_line_move,
            'replace': self.in_line_replace,
            'moved': self.in_line_move
        }

        self.label = {
            'equal': self.label_equal,
            'delete': self.label_delete,
            'insert': self.label_insert,
            'move': self.label_move,
            'replace': self.label_replace,
            'moved': self.label_move
        }

    def get_line_color(self, tag: str):
        return self.line[tag]

    def get_in_line_color(self, tag: str):
        return self.in_line[tag]

    def get_label_color(self, tag: str):
        return self.label[tag]


console_colors_fore = ConsoleColors(
    line_delete=colorama.Fore.RED,
    line_insert=colorama.Fore.GREEN,
    line_move=colorama.Fore.BLUE,
    line_replace=colorama.Fore.YELLOW,
    line_equal=colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL,
    line_filler=colorama.Fore.LIGHTBLACK_EX + colorama.Style.DIM,
    in_line_delete=colorama.Fore.RED,
    in_line_insert=colorama.Fore.GREEN,
    in_line_move=colorama.Fore.BLUE,
    in_line_replace=colorama.Fore.RED,
    in_line_equal='',
    label_equal=colorama.Fore.RESET + colorama.Back.RESET,
    label_delete=colorama.Fore.RED,
    label_insert=colorama.Fore.GREEN,
    label_move=colorama.Fore.BLUE,
    label_replace=colorama.Fore.YELLOW
)

console_colors_back = ConsoleColors(
    line_delete=colorama.Back.RED + colorama.Fore.RESET,
    line_insert=colorama.Back.GREEN + colorama.Fore.RESET,
    line_move=colorama.Back.BLUE + colorama.Fore.RESET,
    line_replace=colorama.Back.YELLOW + colorama.Fore.RESET,
    line_equal=colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL,
    line_filler=colorama.Back.LIGHTBLACK_EX + colorama.Style.DIM,
    in_line_delete=colorama.Back.RED,
    in_line_insert=colorama.Back.GREEN,
    in_line_move=colorama.Back.BLUE,
    in_line_replace=colorama.Back.RED,
    in_line_equal='',
    label_equal=colorama.Fore.RESET + colorama.Back.RESET,
    label_delete=colorama.Fore.RED,
    label_insert=colorama.Fore.GREEN,
    label_move=colorama.Fore.BLUE,
    label_replace=colorama.Fore.YELLOW,
)

ascii_console_characters = ConsoleCharacters(
    sep_line_num='|',
    symbol_line_equal=' ',
    symbol_line_delete='-',
    symbol_line_insert='+',
    symbol_line_move='M',
    symbol_line_move_up='^',
    symbol_line_move_down='v',
    symbol_line_replace='R',
    symbol_line_similar='~',
    line_fill_char=' '
)

unicode_console_characters = ConsoleCharacters(
    sep_line_num='│',
    symbol_line_equal=' ',
    symbol_line_delete='−',
    symbol_line_insert='+',
    symbol_line_move='⇅',
    symbol_line_move_up='🠕',
    symbol_line_move_down='🠗',
    symbol_line_replace='≠',
    symbol_line_similar='≠',
    line_fill_char=' '
)
# ǀ ≠ 🠕 🠗 ⇅

console_colors: Dict[str, ConsoleColors] = {
    'fore': console_colors_fore,
    'back': console_colors_back
}

console_characters: Dict[str, ConsoleCharacters] = {
    'ascii': ascii_console_characters,
    'utf8': unicode_console_characters
}


def get_console_colors(color_mode: str):
    return console_colors[color_mode]


def get_console_characters(char_set: str):
    return console_characters[char_set]


def longest_string_in_list(s_list: Sequence[str]):
    return max(s_list, key=lambda x: len(x))


def digits_number(a: int):
    return int(log10(a)) + 1


class ConsolePrinter(abc.ABC):
    @abc.abstractmethod
    def print(self):
        pass


class LineDiffConsolePrinter:
    def __init__(self, a: Sequence[str], b: Sequence[str], seq: Sequence[CompositeOpCode],
                 characters: ConsoleCharacters, colors: ConsoleColors,
                 line_margin=3, equal_context=-1, op_char_space=1):
        self.a = a
        self.b = b
        self.seq = seq
        self.characters = characters
        self.colors = colors
        self.line_margin = line_margin
        self.equal_context = equal_context
        self.op_char_space = op_char_space

        # build formatting
        self.longest_string_len = {
            'a': len(longest_string_in_list(self.a)),
            'b': len(longest_string_in_list(self.b))
        }

        self.line_digits_number = {
            'a': digits_number(len(self.a)),
            'b': digits_number(len(self.b))
        }

        self.op_chars = {
            'equal': ('', ''),
            'insert': ('', self.characters.get_op_char('insert')),
            'delete': (self.characters.get_op_char('delete'), ''),
            'move': (self.characters.get_op_char('move'), ''),
            'moved': ('', self.characters.get_op_char('moved')),
            'replace': (self.characters.get_op_char('replace'), self.characters.get_op_char('replace'))
        }

    def get_line_digits_number(self, side: Literal['a', 'b']):
        return self.line_digits_number[side]

    def get_longest_string_len(self, side: Literal['a', 'b']):
        return self.longest_string_len[side]

    def get_op_char(self, tag: str, side: Literal['a', 'b']):
        if side == 'a':
            return self.op_chars[tag][0]
        else:
            return self.op_chars[tag][1]

    def get_line_num(self, curr_idx, opcode: Union[OpCodeType, CompositeOpCode],
                     side: Literal['a', 'b']) -> str:
        tag, i1, i2, j1, j2 = opcode

        if side == 'a':
            if tag in ('delete', 'equal', 'move', 'replace') and curr_idx < (i2 - i1):
                return i1 + curr_idx + 1
        else:
            if tag in ('insert', 'equal', 'moved', 'replace') and curr_idx < (j2 - j1):
                return j1 + curr_idx + 1
        return ''

    def get_line_num_with_op_char(self, curr_idx, opcode: Union[OpCodeType, CompositeOpCode],
                                  side: Literal['a', 'b']) -> Tuple[str, str]:
        line_num = self.get_line_num(curr_idx, opcode, side)
        tag, *_ = opcode
        op_char = self.get_op_char(tag, side) if line_num else ''
        return line_num, op_char

    def get_label_string(self, line_num: str, op_char: str, opcode: Union[OpCodeType, CompositeOpCode]) -> str:
        reset = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL
        tag, *_ = opcode
        label_style = self.colors.get_label_color(tag)
        label_string = reset + f'{self.characters.sep_line_num} ' + label_style \
                       + f'{line_num:>{self.get_line_digits_number("a")}}' + f'{op_char:>{self.op_char_space}}' \
                       + reset + f'{self.characters.sep_line_num}'
        return label_string

    def get_line_string(self, line: str, opcode: Union[OpCodeType, CompositeOpCode], side: Literal['a', 'b']) -> str:
        if side == 'a':
            get_opcode_start_idx = itemgetter(1)
            get_opcode_end_idx = itemgetter(2)
            tags = ('delete', 'move', 'replace')
        else:
            get_opcode_start_idx = itemgetter(3)
            get_opcode_end_idx = itemgetter(4)
            tags = ('insert', 'moved', 'replace')

        line_tag, *_ = opcode
        line_style = self.colors.get_line_color(line_tag)

        if isinstance(opcode, CompositeOpCode) and opcode.children_opcodes:
            line_content_parts = []
            for child_opcode in opcode.children_opcodes:
                tag, *_ = child_opcode
                i1 = get_opcode_start_idx(child_opcode)
                i2 = get_opcode_end_idx(child_opcode)
                if tag in tags:
                    in_line_style = self.colors.get_in_line_color(tag)
                    line_content_parts.append(in_line_style + line[i1:i2])
                else:
                    # keep print style on a line level (note that there is no 'equal' in tags variable)
                    line_content_parts.append(line_style + line[i1:i2])
            line_content_parts.append(line_style)
            line_content = ''.join(line_content_parts)
        else:
            if line_tag in tags:
                line_content = line_style + line
            else:
                line_content = line

        if line_tag in ('equal', 'insert', 'moved'):
            line_fill_char = ' '
        else:
            line_fill_char = self.characters.line_fill_char
        output = line_content + (line_fill_char * (self.get_longest_string_len(side) - len(line) + self.line_margin))
        return output

    def print_entry(self, opcode: Union[OpCodeType, CompositeOpCode], curr_opcode_index: int,
                    a_line_content: str = '', b_line_content: str = '') -> None:
        tag, i1, i2, j1, j2 = opcode

        if tag == 'replace' and not (isinstance(opcode, CompositeOpCode) and opcode.children_opcodes):
            opcode_delete = OpCode(*opcode)
            opcode_delete.tag = 'delete'
            a_line_num, a_op_char = self.get_line_num_with_op_char(curr_opcode_index, opcode_delete, 'a')

            opcode_insert = OpCode(*opcode)
            opcode_insert.tag = 'insert'
            b_line_num, b_op_char = self.get_line_num_with_op_char(curr_opcode_index, opcode_insert, 'b')

            opcode_equal = OpCode(*opcode)
            opcode_equal.tag = 'equal'

            if curr_opcode_index >= (i2 - i1):
                opcode_delete = opcode_equal

            if curr_opcode_index >= (j2 - j1):
                opcode_insert = opcode_equal

            a_label_s = self.get_label_string(line_num=a_line_num, op_char=a_op_char, opcode=opcode_delete)
            a_content = self.get_line_string(line=a_line_content, opcode=opcode_delete, side='a')
            b_label_s = self.get_label_string(line_num=b_line_num, op_char=b_op_char, opcode=opcode_insert)
            b_content = self.get_line_string(line=b_line_content, opcode=opcode_insert, side='b')

        else:
            a_line_num, a_op_char = self.get_line_num_with_op_char(curr_opcode_index, opcode, 'a')
            b_line_num, b_op_char = self.get_line_num_with_op_char(curr_opcode_index, opcode, 'b')

            a_label_s = self.get_label_string(line_num=a_line_num, op_char=a_op_char, opcode=opcode)
            a_content = self.get_line_string(line=a_line_content, opcode=opcode, side='a')
            b_label_s = self.get_label_string(line_num=b_line_num, op_char=b_op_char, opcode=opcode)
            b_content = self.get_line_string(line=b_line_content, opcode=opcode, side='b')
        print(f'{a_label_s}{a_content}{b_label_s}{b_content}{STYLE_RESET}')

    def print_opcode(self, opcode: OpCodeType):
        tag, i1, i2, j1, j2 = opcode
        if tag == 'equal':
            for idx, (left, right) in enumerate(zip(self.a[i1:i2], self.b[j1:j2])):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content=left,
                    b_line_content=right
                )
        if tag == 'insert':
            for idx, right in enumerate(self.b[j1:j2]):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content='',
                    b_line_content=right
                )
        if tag == 'delete':
            for idx, left in enumerate(self.a[i1:i2]):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content=left,
                    b_line_content=''
                )

        if tag == 'replace':
            for idx, (left, right) in enumerate(zip_longest(self.a[i1:i2], self.b[j1:j2], fillvalue='')):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content=left,
                    b_line_content=right
                )

        if tag == 'move':
            for idx, left in enumerate(self.a[i1:i2]):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content=left,
                    b_line_content=''
                )
        if tag == 'moved':
            for idx, right in enumerate(self.b[j1:j2]):
                self.print_entry(
                    opcode=opcode,
                    curr_opcode_index=idx,
                    a_line_content='',
                    b_line_content=right
                )

    def print(self):
        colorama.init(autoreset=False, convert=True)
        for opcode in self.seq:
            self.print_opcode(opcode)
        print(colorama.Fore.RESET + colorama.Back.RESET)
        colorama.deinit()
