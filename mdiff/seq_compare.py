from abc import abstractmethod
from collections import Sequence
from dataclasses import dataclass
from enum import Enum
from itertools import zip_longest
from typing import List, Any, Callable, Optional, overload, Union, TypeVar


def _identity_eq(a, b) -> bool:
    return a == b


T = TypeVar('T')


class KeyCompareStatus(str, Enum):
    OK = 'ok'
    OUT_OF_ORDER = 'order'
    MISSING = 'missing'
    EXCESSIVE = 'excessive'

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


@dataclass(eq=True)
class KeyComparisonResultEntry:
    source_key: Any
    target_key: Any
    missing_keys_offset: int
    absolute_offset: int
    relative_offset: int
    status: KeyCompareStatus


class KeyComparisonResult(Sequence):
    def __init__(self, data: List[KeyComparisonResultEntry]):
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx) -> Union[KeyComparisonResultEntry, Sequence[KeyComparisonResultEntry]]:
        return self.data[idx]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data})"

    def __eq__(self, other):
        return self.data == other.data


class GenericSequenceComparator:
    """
    Compares target sequence to a source sequence and finds potential differences.

    Sequences Assumptions:
    * sequence elements are comparable
    * sequence elements are hashable
    * sequence elements are unique
    """

    def __init__(self, source_keys: List[T], target_keys: List[T]):
        self.source_keys = source_keys
        self.target_keys = target_keys
        self.source_keys_dict = {key: i for i, key in enumerate(self.source_keys)}
        self.target_keys_dict = {key: i for i, key in enumerate(self.target_keys)}

    def _get_index_of_element_in_dict(self, element, lst):
        return lst.get(element)


    def _get_element_at_index_in_list(self, index, lst) -> Optional[int]:
        try:
            element = lst[index]
        except IndexError:
            element = None
        return element




    def compare_sequences(self) -> KeyComparisonResult:
        missing_keys_offset = 0
        tgt_seq_idx = 0
        src_seq_idx = 0
        result = []

        while src_seq_idx < len(self.source_keys) or tgt_seq_idx < len(self.target_keys):
            # Take elements under indexes
            src_key = self._get_element_at_index_in_list(src_seq_idx, self.source_keys)
            tgt_key = self._get_element_at_index_in_list(tgt_seq_idx, self.target_keys)
            # And check if they exists in opposite sequences
            tgt_elem_idx_in_src = self._get_index_of_element_in_dict(tgt_key, self.source_keys_dict)
            src_elem_idx_in_tgt = self._get_index_of_element_in_dict(src_key, self.target_keys_dict)
            tgt_elem_idx_in_tgt = tgt_seq_idx

            # If both corresponding elements exist in opposite sequences
            if tgt_elem_idx_in_src is not None and src_elem_idx_in_tgt is not None:
                abs_offset = tgt_elem_idx_in_tgt - tgt_elem_idx_in_src
                rel_offset = abs_offset - missing_keys_offset
                status = KeyCompareStatus.OK if rel_offset == 0 else KeyCompareStatus.OUT_OF_ORDER
                result.append(KeyComparisonResultEntry(
                    source_key=src_key,
                    target_key=tgt_key,
                    missing_keys_offset=missing_keys_offset,
                    absolute_offset=abs_offset,
                    relative_offset=rel_offset,
                    status=status
                ))
                src_seq_idx += 1
                tgt_seq_idx += 1
                continue

            # If both elements don't exist in opposite sequences, but not because either of indexes reached max
            # or only source element doesn't exists in target sequence
            if (tgt_elem_idx_in_src is None and src_elem_idx_in_tgt is None and not (
                    src_key is None or tgt_key is None)) \
                    or (src_elem_idx_in_tgt is None and src_key is not None):
                result.append(KeyComparisonResultEntry(
                    source_key=src_key,
                    target_key=None,
                    missing_keys_offset=missing_keys_offset,
                    absolute_offset=None,
                    relative_offset=None,
                    status=KeyCompareStatus.MISSING
                ))
                src_seq_idx += 1
                missing_keys_offset -= 1
                continue

                # If only target element doesn't exists in source sequence
            if tgt_elem_idx_in_src is None and tgt_key is not None:
                result.append(KeyComparisonResultEntry(
                    source_key=None,
                    target_key=tgt_key,
                    missing_keys_offset=missing_keys_offset,
                    absolute_offset=None,
                    relative_offset=None,
                    status=KeyCompareStatus.EXCESSIVE
                ))
                tgt_seq_idx += 1
                missing_keys_offset += 1
                continue

        return KeyComparisonResult(result)


# some tests with comparison and hash


class MyContainer(Sequence):
    def __init__(self, data_list):
        self.data_list = data_list

    def __getitem__(self, i: int):
        return self.data_list[i]

    def __len__(self):
        return len(self.data_list)
