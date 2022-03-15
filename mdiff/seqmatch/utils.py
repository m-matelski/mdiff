from difflib import SequenceMatcher
from enum import Enum
from typing import Type

from mdiff.seqmatch.heckel import HeckelSequenceMatcher, DisplacementSequenceMatcher
from mdiff.utils import SequenceMatcherBase


class SequenceMatcherName(str, Enum):
    STANDARD = 'standard'
    HECKEL = 'heckel'
    DISPLACEMENT = 'displacement'


seq_matchers = {
    SequenceMatcherName.STANDARD: SequenceMatcher,
    SequenceMatcherName.HECKEL: HeckelSequenceMatcher,
    SequenceMatcherName.DISPLACEMENT: DisplacementSequenceMatcher,
}


def seq_matcher_factory(seq_matcher_type: SequenceMatcherName) -> Type[SequenceMatcherBase]:
    values = SequenceMatcherName.__dict__.values()
    if seq_matcher_type not in values:
        raise ValueError(f'seq_matcher_type must be in: {values}')
    return seq_matchers[seq_matcher_type]
