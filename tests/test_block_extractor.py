import unittest

from mdiff.block_extractor import ConsecutiveIntegerBlockExtractor, NonIntegersBlockExtractor, \
    OpCodeDeleteThenInsertBlockExtractor, ConsecutiveVectorBlockExtractor
from mdiff.utils import OpCode


class TestConsecutiveIntegerBlockExtractor(unittest.TestCase):

    def test_mixed_types(self):
        seq = [1, 2, 3, 's', 7, 8, 's', 5]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 3), (4, 2), (7, 1)]
        self.assertEqual(expected_blocks, blocks)

    def test_unordered_ints(self):
        seq = [6, 5, 1, 2, 9, 7, 8, 4]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 1), (1, 1), (2, 2), (4, 1), (5, 2), (7, 1)]
        self.assertEqual(expected_blocks, blocks)

    def test_empty(self):
        seq = []
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = []
        self.assertEqual(expected_blocks, blocks)

    def test_one_element_seq(self):
        seq = [1]
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 1)]
        self.assertEqual(expected_blocks, blocks)

    def test_no_ints_in_seq(self):
        seq = ['a', 'b', 'c']
        be = ConsecutiveIntegerBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = []
        self.assertEqual(expected_blocks, blocks)


class TestConsecutiveVectorBlockExtractor(unittest.TestCase):
    def test1(self):
        seq = [[0, 0], [1, 1], [2, 3], [2, 4], [4, 6], [5, 7], [1, 1], [2, 2], [4, 4]]
        be = ConsecutiveVectorBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 2), (2, 1), (3, 1), (4, 2), (6, 2), (8, 1)]
        self.assertEqual(expected_blocks, blocks)


class TestNonIntegersBlockExtractor(unittest.TestCase):
    def test1(self):
        seq = [1, 2, 3, 'a', 'b', 4, 'c']
        be = NonIntegersBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(3, 2), (6, 1)]
        self.assertEqual(expected_blocks, blocks)


class TestDeleteThenInsertBlockExtractor(unittest.TestCase):

    def test_finishing_in_block(self):
        """
        Test if block extractor doesn't return invalid block when input sequence ends with delete
        (block start condition)
        """
        seq = [OpCode('delete', 0, 0, 0, 0),
               OpCode('insert', 0, 0, 0, 0),
               OpCode('equal', 0, 0, 0, 0),
               OpCode('delete', 0, 0, 0, 0)]

        be = OpCodeDeleteThenInsertBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 2)]
        self.assertEqual(expected_blocks, blocks)

    def test_delete_insert_at_the_end(self):
        """Test if block extractor returns replace block when insert, and delete are 2 last entries in the sequence."""
        seq = [OpCode('delete', 0, 0, 0, 0),
               OpCode('insert', 0, 0, 0, 0),
               OpCode('equal', 0, 0, 0, 0),
               OpCode('delete', 0, 0, 0, 0),
               OpCode('insert', 0, 0, 0, 0)]

        be = OpCodeDeleteThenInsertBlockExtractor(seq)
        blocks = list(be.extract_blocks())
        expected_blocks = [(0, 2), (3, 2)]
        self.assertEqual(expected_blocks, blocks)
