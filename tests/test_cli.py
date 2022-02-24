import unittest
from pathlib import Path

from mdiff.cli import cli_diff


class TestCLI(unittest.TestCase):

    def test1(self):
        cli_diff(source_file=Path('tests/resources/compares/comp1/a.txt'),
                 target_file=Path('tests/resources/compares/comp1/b.txt'),
                 line_sm_name='heckel',
                 similarities_sm_name='standard',
                 cutoff=0.75,
                 char_mode='utf8'
                 )
