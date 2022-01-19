from abc import ABC, abstractmethod
from collections import Sequence
from typing import Any, TypeVar


def sequences_equal(a, b) -> bool:
    return tuple(a) == tuple(b)


T = TypeVar('T')


class BaseBlockExtractor(ABC):

    def __init__(self, seq: Sequence[T]):
        self.prev = None
        self.block_start_idx = 0
        self.block_len = 0
        self.in_block = False

        self.seq = seq

    def _setup(self):
        self.prev = None
        self.block_start_idx = 0
        self.block_len = 0
        self.in_block = False

    def _seq_iterator(self):
        return (i for i in self.seq)

    @abstractmethod
    def _open_block_cond(self, prev, curr) -> bool:
        pass

    @abstractmethod
    def _close_block_cond(self, prev, curr) -> bool:
        pass

    def _return_block(self, block_start_idx, block_len):
        return block_start_idx, block_len

    def extract_blocks(self):
        self._setup()
        for idx, i in enumerate(self._seq_iterator()):
            # close block
            if not self.prev is None and self._close_block_cond(self.prev, i) and self.in_block:
                yield self._return_block(self.block_start_idx, self.block_len)
                self.in_block = False
            # open block
            if not self.in_block and self._open_block_cond(self.prev, i):
                self.block_start_idx = idx
                self.block_len = 0
                self.in_block = True
            # increase block
            self.prev = i
            self.block_len += 1
        # last block
        if self.in_block:
            yield self._return_block(self.block_start_idx, self.block_len)


class ConsecutiveIntegerBlockExtractor(BaseBlockExtractor):

    def _open_block_cond(self, prev, curr) -> bool:
        return isinstance(curr, int)

    def _close_block_cond(self, prev, curr) -> bool:
        try:
            return curr != prev + 1
        except TypeError:
            return True


class ConsecutiveVectorBlockExtractor(BaseBlockExtractor):
    def _open_block_cond(self, prev, curr) -> bool:
        return True

    def _close_block_cond(self, prev, curr) -> bool:
        try:
            prev_plus_one = [i + 1 for i in prev]
            return not sequences_equal(curr, prev_plus_one)
        except TypeError:
            return True


class HeckelSequenceNonUniqueEntriesBlockExtractor(BaseBlockExtractor):

    def _open_block_cond(self, prev, curr) -> bool:
        return not isinstance(curr, int)

    def _close_block_cond(self, prev, curr) -> bool:
        return isinstance(curr, int)


class HeckelDeleteThenInsertBlockExtractor(BaseBlockExtractor):

    def _open_block_cond(self, prev, curr) -> bool:
        return curr.tag == 'delete'

    def _close_block_cond(self, prev, curr) -> bool:
        if curr.tag == 'insert':
            return True
        else:
            self.in_block = False
            return False

    def _return_block(self, block_start_idx, block_len):
        return super(HeckelDeleteThenInsertBlockExtractor, self)._return_block(block_start_idx, 2)
