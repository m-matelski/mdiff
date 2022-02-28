import unittest
from difflib import SequenceMatcher
from pathlib import Path

from mdiff import diff_lines_with_similarities, HeckelSequenceMatcher
from mdiff.seqmatch.heckel import DisplacementSequenceMatcher
from mdiff.utils import read_file


class TestTextDiff(unittest.TestCase):

    def test1(self):
        a = read_file(Path('tests/resources/compares/comp3/a.txt'))
        b = read_file(Path('tests/resources/compares/comp3/b.txt'))
        a_lines, b_lines, opcodes = diff_lines_with_similarities(a, b)
        sm = SequenceMatcher(a=a_lines, b=b_lines)
        hopcodes = sm.get_opcodes()
        x = 1
