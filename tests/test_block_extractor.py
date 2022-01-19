import unittest

from mdiff.block_extractor import ConsecutiveIntegerBlockExtractor, HeckelSequenceNonUniqueEntriesBlockExtractor


class TestConsecutiveIntegerBlockExtractor(unittest.TestCase):

    def test_mixed_types(self):
        seq = [1, 2, 3, 's', 7, 8, 's', 5]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 3), (4, 2), (7, 1)]
        self.assertEqual(blocks, expected_blocks)

    def test_unordered_ints(self):
        seq = [6, 5, 1, 2, 9, 7, 8, 4]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 1), (1, 1), (2, 2), (4, 1), (5, 2), (7, 1)]
        self.assertEqual(blocks, expected_blocks)

    def test_empty(self):
        seq = []
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = []
        self.assertEqual(blocks, expected_blocks)

    def test_one_element_seq(self):
        seq = [1]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 1)]
        self.assertEqual(blocks, expected_blocks)

    def test_no_ints_in_seq(self):
        seq = ['a', 'b', 'c']
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = []
        self.assertEqual(blocks, expected_blocks)


class TestHeckelSequenceNonUniqueEntriesBlockExtractor(unittest.TestCase):
    def test1(self):
        seq = [1, 2, 3, 'a', 'b', 4, 'c']
        be = HeckelSequenceNonUniqueEntriesBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(3, 2), (6, 1)]
