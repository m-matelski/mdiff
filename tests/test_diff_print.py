import unittest
from difflib import SequenceMatcher
from pathlib import Path

from mdiff.seqmatch.heckel import DisplacementSequenceMatcher, HeckelSequenceMatcher
from mdiff.text_diff import diff_lines_with_similarities
import mdiff.visualisation.terminal as cli_vis
from mdiff.utils import read_file


class TestLineDiffPrint(unittest.TestCase):
    def test_simple_diff_print(self):
        a = 'w11111\nw22222\nw33333\nw44444\nw55555\nw66666'
        b = 'w22229\nw22228\nw44444\nw55555\nw66666'
        line_sm = HeckelSequenceMatcher()
        similarities_sm = SequenceMatcher()
        a_lines, b_lines, opcodes = diff_lines_with_similarities(a=a, b=b, cutoff=0.75,
                                                                 line_sm=line_sm, inline_sm=similarities_sm)
        printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=opcodes,
                                                 characters=cli_vis.unicode_console_characters,
                                                 colors=cli_vis.console_colors_back, line_margin=3, equal_context=-1)
        printer.print()

    def test_diff_print_1(self):
        a = read_file(Path('tests/resources/compares/comp1/a.txt').absolute())
        b = read_file(Path('tests/resources/compares/comp1/b.txt').absolute())
        line_sm = HeckelSequenceMatcher(replace_mode=True)
        similarities_sm = SequenceMatcher()
        a_lines, b_lines, opcodes = diff_lines_with_similarities(a=a, b=b, cutoff=0.75,
                                                                 line_sm=line_sm, inline_sm=similarities_sm)
        printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=list(opcodes),
                                                 characters=cli_vis.unicode_console_characters,
                                                 colors=cli_vis.console_colors_back, line_margin=3, equal_context=-1)
        printer.print()

    def test_diff_print_2(self):
        a = read_file(Path('tests/resources/compares/comp2/a.txt').absolute())
        b = read_file(Path('tests/resources/compares/comp2/b.txt').absolute())
        line_sm = HeckelSequenceMatcher()
        similarities_sm = SequenceMatcher()
        a_lines, b_lines, opcodes = diff_lines_with_similarities(a=a, b=b, cutoff=0.75,
                                                                 line_sm=line_sm, inline_sm=similarities_sm)
        printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=list(opcodes),
                                                 characters=cli_vis.unicode_console_characters,
                                                 colors=cli_vis.console_colors_fore, line_margin=3, equal_context=-1)
        printer.print()
