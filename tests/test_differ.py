import unittest
from pathlib import Path

from mdiff.differ import ConsoleTextDiffer
from mdiff.seqmatch.utils import SequenceMatcherName
from mdiff.utils import read_file


class TestConsoleTextDiffer(unittest.TestCase):

    def test_differ(self):
        source = read_file(Path('tests/resources/compares/comp2/a.txt'))
        target = read_file(Path('tests/resources/compares/comp2/b.txt'))
        differ = ConsoleTextDiffer(a=source,
                                   b=target,
                                   line_sm=SequenceMatcherName.HECKEL,
                                   inline_sm=SequenceMatcherName.HECKEL,
                                   cutoff=0.75,
                                   color_mode='back',
                                   character_mode='ascii',
                                   case_sensitive=True)
        differ.run()
