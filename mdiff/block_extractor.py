"""
This module provides BaseBlockExtractor template method base class and some of it's subclasses implementation.
"""

from abc import ABC, abstractmethod
from collections import Sequence
from typing import Any

from mdiff.utils import sequences_equal, OpCode


class BaseBlockExtractor(ABC):
    """
    This class is a base class that serves as a template method for implementing logic
    to extract blocks (subsequences) of continuous elements in a given sequence.

    Parameters:
        seq: input sequence to detect blocks in.
    """

    def __init__(self, seq: Sequence[Any]):
        self.seq = seq
        # Define attributes
        self._prev = None
        self._block_start_idx = 0
        self._block_len = 0
        self._in_block = False

    def _setup(self):
        """Setup attributes used in algorithm iteration."""
        self._prev = None
        self._block_start_idx = 0
        self._block_len = 0
        self._in_block = False

    def _configure(self):
        """
        Setup config attributes that have impact on algorithm logic.
        Can be overridden in a subclass to change default behaviour.

        Attributes:
            self.yield_last_block:
                Determines if return current block if sequence ends in the middle of detected block. True by default.
        """
        self.yield_last_block = True

    def _seq_iterator(self):
        """Defines a way to iterate through input sequence. Can be overridden."""
        return (i for i in self.seq)

    @abstractmethod
    def _open_block_cond(self, prev, curr) -> bool:
        """
        Override that method in a subclass.
        Defines condition that opens continuous subsequence block.
        """
        pass

    @abstractmethod
    def _close_block_cond(self, prev, curr) -> bool:
        """
        Override that method in a subclass.
        Defines condition that closes continuous subsequence block.
        """
        pass

    def _return_block(self, block_start_idx, block_len):
        """
        Defines way of returning detected block data. Might be overridden.

        By default it returns Tuple of (block_start_idx, block_len) where:
            block_start_idx is an index of block start in a Sequence seq.
            block_len is a length of that block.
        """
        yield block_start_idx, block_len

    def extract_blocks(self):
        """
        Extracts blocks form sequence.

        Returns:
            x:
                Sequence of Tuples(block_start_idx, block_len) where:
                block_start_idx: stores index in sequence where subsequence block starts,
                block_len: stores information about continuous block length.
        """
        self._setup()
        self._configure()
        for idx, i in enumerate(self._seq_iterator()):
            # close block
            if self._prev is not None and self._close_block_cond(self._prev, i) and self._in_block:
                yield from self._return_block(self._block_start_idx, self._block_len)
                self._in_block = False
            # open block
            if not self._in_block and self._open_block_cond(self._prev, i):
                self._block_start_idx = idx
                self._block_len = 0
                self._in_block = True
            # increase block
            self._prev = i
            self._block_len += 1
        # last block
        if self._in_block and self.yield_last_block:
            yield from self._return_block(self._block_start_idx, self._block_len)


class ConsecutiveIntegerBlockExtractor(BaseBlockExtractor):
    """
    Extracts consecutive integer blocks from input sequence. Skips block if non integer value found in a sequence.

    Examples:
        >>> list(ConsecutiveIntegerBlockExtractor([0, 1, 2, 4, 5, 8, 7, 9]).extract_blocks())
        [(0, 3), (3, 2), (5, 1), (6, 1), (7, 1)]

        >>> list(ConsecutiveIntegerBlockExtractor([1, 2, 'a', 3, 4]).extract_blocks())
        [(0, 2), (3, 2)]
    """

    def _open_block_cond(self, prev, curr) -> bool:
        return isinstance(curr, int)

    def _close_block_cond(self, prev, curr) -> bool:
        try:
            return curr != prev + 1
        except TypeError:
            return True


class ConsecutiveVectorBlockExtractor(BaseBlockExtractor):
    """
    Extracts consecutive vector blocks from input sequence.
    Vector means sequence of integers, eg. [1, 1, 1].
    Vector b is consecutive to a when: [a[0]+1, a[1]+1, ..., a[n]+1] == b.
    Skips block if non integer value found in a vector.

    Examples:
        >>> list(ConsecutiveVectorBlockExtractor([[0, 0], [1, 1], [2, 3], [2, 4], [4, 6], [5, 7]]).extract_blocks())
        [(0, 2), (2, 1), (3, 1), (4, 2)]
    """

    def _open_block_cond(self, prev, curr) -> bool:
        return True

    def _close_block_cond(self, prev, curr) -> bool:
        try:
            prev_plus_one = [i + 1 for i in prev]
            return not sequences_equal(curr, prev_plus_one)
        except TypeError:
            return True


class NonIntegersBlockExtractor(BaseBlockExtractor):
    """
    Extracts non integer blocks from input sequence.

    Examples:
        >>> list(NonIntegersBlockExtractor([0, 1, 'a', 2, 'b', 'c', 3, 4]).extract_blocks())
        [(2, 1), (4, 2)]
    """

    def _open_block_cond(self, prev, curr) -> bool:
        return not isinstance(curr, int)

    def _close_block_cond(self, prev, curr) -> bool:
        return isinstance(curr, int)


class OpCodeDeleteThenInsertBlockExtractor(BaseBlockExtractor):
    """
    Extracts 2-element blocks from given opcodes sequence where first opcode tag is "insert" and second is "delete".

    Examples:
        >>> opcodes = [\
            OpCode('delete', 0, 0, 0, 0), \
            OpCode('equal', 0, 0, 0, 0), \
            OpCode('delete', 0, 0, 0, 0),\
            OpCode('insert', 0, 0, 0, 0),\
            OpCode('delete', 0, 0, 0, 0)]
        >>> list(OpCodeDeleteThenInsertBlockExtractor(opcodes).extract_blocks())
        [(2, 2)]
    """

    def __init__(self, seq: Sequence[OpCode]):
        super().__init__(seq)

    def _configure(self):
        super()._configure()
        self.yield_last_block = False

    def _open_block_cond(self, prev, curr) -> bool:
        return curr.tag == 'delete'

    def _close_block_cond(self, prev, curr) -> bool:
        if curr.tag == 'insert':
            return True
        else:
            self._in_block = False
            return False

    def _return_block(self, block_start_idx, block_len):
        return super(OpCodeDeleteThenInsertBlockExtractor, self)._return_block(block_start_idx, 2)


class EmptyStringBlockExtractor(BaseBlockExtractor):
    """
    Extracts consecutive empty strings in sequence.

    Examples:
        >>> list(EmptyStringBlockExtractor(['a', 'b', '', 'c', '', '', 'd', '']).extract_blocks())
        [(2, 1), (4, 2), (7, 1)]
    """
    def _open_block_cond(self, prev, curr) -> bool:
        return curr == ''

    def _close_block_cond(self, prev, curr) -> bool:
        return curr != ''
