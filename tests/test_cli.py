import unittest
from pathlib import Path

from mdiff.cli import cli_diff, SequenceMatcherName, ColorMode, CharacterMode


class TestCLI(unittest.TestCase):

    def test1(self):
        cli_diff(source_file=Path('tests/resources/compares/comp1/a.txt'),
                 target_file=Path('tests/resources/compares/comp1/b.txt'),
                 line_sm=SequenceMatcherName.HECKEL,
                 inline_sm=SequenceMatcherName.STANDARD,
                 cutoff=0.75,
                 char_mode=CharacterMode.UTF8,
                 color_mode=ColorMode.FORE
                 )
