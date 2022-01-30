import unittest

from mdiff.seqmatch.heckel import HeckelSequenceMatcher
from mdiff.utils import OpCode


class TestHeckelSequenceMatcher(unittest.TestCase):

    def test_heckel_paper_example(self):
        a = ["MUCH", "WRITING", "IS", "LIKE", "SNOW", ",",
             "A", "MASS", "OF", "LONG", "WORDS", "AND",
             "PHRASES", "FALLS", "UPON", "THE", "RELEVANT",
             "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]

        b = ["A", "MASS", "OF", "LATIN", "WORDS", "FALLS",
             "UPON", "THE", "RELEVANT", "FACTS", "LIKE", "SOFT",
             "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='delete', i1=0, i2=3, j1=0, j2=0),
                            OpCode(tag='move', i1=3, i2=4, j1=10, j2=10),
                            OpCode(tag='move', i1=4, i2=6, j1=12, j2=12),
                            OpCode(tag='equal', i1=6, i2=9, j1=0, j2=3),
                            OpCode(tag='delete', i1=9, i2=10, j1=3, j2=3),
                            OpCode(tag='insert', i1=10, i2=10, j1=3, j2=4),
                            OpCode(tag='equal', i1=10, i2=11, j1=4, j2=5),
                            OpCode(tag='delete', i1=11, i2=13, j1=5, j2=5),
                            OpCode(tag='equal', i1=13, i2=18, j1=5, j2=10),
                            OpCode(tag='moved', i1=3, i2=3, j1=10, j2=11),
                            OpCode(tag='insert', i1=18, i2=18, j1=11, j2=12),
                            OpCode(tag='moved', i1=4, i2=4, j1=12, j2=14),
                            OpCode(tag='equal', i1=18, i2=23, j1=14, j2=19)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_common_elements_sequences_comparison(self):
        a = ["LIKE", "SNOW", ",",
             "A", "MASS", "OF", "WORDS",
             "FALLS", "UPON", "THE", "RELEVANT",
             "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]

        b = ["A", "MASS", "OF", "WORDS", "FALLS",
             "UPON", "THE", "RELEVANT", "FACTS", "LIKE",
             "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='move', i1=0, i2=3, j1=9, j2=9),
                            OpCode(tag='equal', i1=3, i2=12, j1=0, j2=9),
                            OpCode(tag='moved', i1=0, i2=0, j1=9, j2=12),
                            OpCode(tag='equal', i1=12, i2=17, j1=12, j2=17)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_1(self):
        a = 'f1 f2 f7 f8 f9 f4 f5 f11 f4 f5'.split()
        b = 'f1 f2 f3 f4 f7 f8 f9 f10 f5 f3 f4 f5'.split()

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='equal', i1=0, i2=2, j1=0, j2=2),
                            OpCode(tag='insert', i1=2, i2=2, j1=2, j2=4),
                            OpCode(tag='equal', i1=2, i2=5, j1=4, j2=7),
                            OpCode(tag='delete', i1=5, i2=10, j1=7, j2=7),
                            OpCode(tag='insert', i1=10, i2=10, j1=7, j2=12)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_2(self):
        a = [1, 1, 0, 3, 0]
        b = [0, 3, 2, 4, 1, 1]

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='delete', i1=0, i2=2, j1=0, j2=0),
                            OpCode(tag='equal', i1=2, i2=4, j1=0, j2=2),
                            OpCode(tag='delete', i1=4, i2=5, j1=2, j2=2),
                            OpCode(tag='insert', i1=5, i2=5, j1=2, j2=6)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_3(self):
        a = [3, 0, 1, 6, 6, 0, 4, 6, 1, 6, 3]
        b = [5, 8, 7, 5, 7, 4, 7, 3, 4, 7, 6]

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='delete', i1=0, i2=11, j1=0, j2=0),
                            OpCode(tag='insert', i1=11, i2=11, j1=0, j2=11)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_reversed(self):
        a = [1, 2, 3, 4, 5]
        b = [5, 4, 3, 2, 1]

        hd = HeckelSequenceMatcher(a, b, replace_mode=False)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='move', i1=0, i2=1, j1=4, j2=4),
                            OpCode(tag='move', i1=1, i2=2, j1=3, j2=3),
                            OpCode(tag='move', i1=2, i2=3, j1=2, j2=2),
                            OpCode(tag='move', i1=3, i2=4, j1=1, j2=1),
                            OpCode(tag='equal', i1=4, i2=5, j1=0, j2=1),
                            OpCode(tag='moved', i1=3, i2=3, j1=1, j2=2),
                            OpCode(tag='moved', i1=2, i2=2, j1=2, j2=3),
                            OpCode(tag='moved', i1=1, i2=1, j1=3, j2=4),
                            OpCode(tag='moved', i1=0, i2=0, j1=4, j2=5)]
        self.assertEqual(expected_opcodes, opcodes)


class TestHeckelSequenceMatcherWithReplaceTag(unittest.TestCase):

    def test_heckel_paper_example(self):
        a = ["MUCH", "WRITING", "IS", "LIKE", "SNOW", ",",
             "A", "MASS", "OF", "LONG", "WORDS", "AND",
             "PHRASES", "FALLS", "UPON", "THE", "RELEVANT",
             "FACTS", "COVERING", "UP", "THE", "DETAILS", "."]

        b = ["A", "MASS", "OF", "LATIN", "WORDS", "FALLS",
             "UPON", "THE", "RELEVANT", "FACTS", "LIKE", "SOFT",
             "SNOW", ",", "COVERING", "UP", "THE", "DETAILS", "."]

        hd = HeckelSequenceMatcher(a, b, replace_mode=True)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='delete', i1=0, i2=3, j1=0, j2=0),
                            OpCode(tag='move', i1=3, i2=4, j1=10, j2=10),
                            OpCode(tag='move', i1=4, i2=6, j1=12, j2=12),
                            OpCode(tag='equal', i1=6, i2=9, j1=0, j2=3),
                            OpCode(tag='replace', i1=9, i2=10, j1=3, j2=4),
                            OpCode(tag='equal', i1=10, i2=11, j1=4, j2=5),
                            OpCode(tag='delete', i1=11, i2=13, j1=5, j2=5),
                            OpCode(tag='equal', i1=13, i2=18, j1=5, j2=10),
                            OpCode(tag='moved', i1=3, i2=3, j1=10, j2=11),
                            OpCode(tag='insert', i1=18, i2=18, j1=11, j2=12),
                            OpCode(tag='moved', i1=4, i2=4, j1=12, j2=14),
                            OpCode(tag='equal', i1=18, i2=23, j1=14, j2=19)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_1(self):
        a = 'f1 f2 f7 f8 f9 f4 f5 f11 f4 f5'.split()
        b = 'f1 f2 f3 f4 f7 f8 f9 f10 f5 f3 f4 f5'.split()

        hd = HeckelSequenceMatcher(a, b, replace_mode=True)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='equal', i1=0, i2=2, j1=0, j2=2),
                            OpCode(tag='insert', i1=2, i2=2, j1=2, j2=4),
                            OpCode(tag='equal', i1=2, i2=5, j1=4, j2=7),
                            OpCode(tag='replace', i1=5, i2=10, j1=7, j2=12)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_2(self):
        a = [1, 1, 0, 3, 0]
        b = [0, 3, 2, 4, 1, 1]

        hd = HeckelSequenceMatcher(a, b, replace_mode=True)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='delete', i1=0, i2=2, j1=0, j2=0),
                            OpCode(tag='equal', i1=2, i2=4, j1=0, j2=2),
                            OpCode(tag='replace', i1=4, i2=5, j1=2, j2=6)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_edge_case_3(self):
        a = [3, 0, 1, 6, 6, 0, 4, 6, 1, 6, 3]
        b = [5, 8, 7, 5, 7, 4, 7, 3, 4, 7, 6]

        hd = HeckelSequenceMatcher(a, b, replace_mode=True)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='replace', i1=0, i2=11, j1=0, j2=11)]
        self.assertEqual(expected_opcodes, opcodes)

    def test_reversed(self):
        a = [1, 2, 3, 4, 5]
        b = [5, 4, 3, 2, 1]

        hd = HeckelSequenceMatcher(a, b, replace_mode=True)
        opcodes = hd.get_opcodes()
        expected_opcodes = [OpCode(tag='move', i1=0, i2=1, j1=4, j2=4),
                            OpCode(tag='move', i1=1, i2=2, j1=3, j2=3),
                            OpCode(tag='move', i1=2, i2=3, j1=2, j2=2),
                            OpCode(tag='move', i1=3, i2=4, j1=1, j2=1),
                            OpCode(tag='equal', i1=4, i2=5, j1=0, j2=1),
                            OpCode(tag='moved', i1=3, i2=3, j1=1, j2=2),
                            OpCode(tag='moved', i1=2, i2=2, j1=2, j2=3),
                            OpCode(tag='moved', i1=1, i2=1, j1=3, j2=4),
                            OpCode(tag='moved', i1=0, i2=0, j1=4, j2=5)]
        self.assertEqual(expected_opcodes, opcodes)
