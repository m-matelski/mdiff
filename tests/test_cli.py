import unittest
from pathlib import Path

import typer
from typer.testing import CliRunner

from mdiff.cli import cli_diff, SequenceMatcherName, ColorMode, CharacterMode

runner = CliRunner()


class TestCLI(unittest.TestCase):

    def test_cli_run_using_arguments(self):
        """Test if diff works from cli level"""
        cli_diff(source_file=Path('tests/resources/compares/comp1/a.txt'),
                 target_file=Path('tests/resources/compares/comp1/b.txt'),
                 line_sm=SequenceMatcherName.HECKEL,
                 inline_sm=SequenceMatcherName.STANDARD,
                 cutoff=0.75,
                 char_mode=CharacterMode.UTF8,
                 color_mode=ColorMode.FORE
                 )

    def test_cli_run(self):
        """Test if mdiff cli works"""
        app = typer.Typer()
        app.command()(cli_diff)
        result = runner.invoke(app,
                               ['tests/resources/compares/comp1/a.txt', 'tests/resources/compares/comp1/b.txt'])
        self.assertEqual(result.exit_code, 0)
