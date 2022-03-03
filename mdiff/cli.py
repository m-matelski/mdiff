from enum import Enum
from pathlib import Path

import typer

from mdiff.seqmatch.utils import seq_matcher_factory
from mdiff.text_diff import diff_lines_with_similarities
import mdiff.visualisation.terminal as cli_vis
from mdiff.utils import read_file

sm_valid_names = ('standard', 'heckel', 'displacement')


class StringEnumChoice(str, Enum):
    """
    Base class for typer choice enum strings. Predefined __str__ method fixes the bug where
    default showed StringEnumChoice.value instead of value
    """

    def __str__(self):
        return self.value


class SequenceMatcherName(StringEnumChoice):
    STANDARD = 'standard'
    HECKEL = 'heckel'
    DISPLACEMENT = 'displacement'


class CharacterMode(StringEnumChoice):
    UTF8 = 'utf8'
    ASCII = 'ascii'


class ColorMode(StringEnumChoice):
    FORE = 'fore'
    BACK = 'back'


def cli_diff(source_file: Path = typer.Argument(..., help="Source file path to compare."),
             target_file: Path = typer.Argument(..., help="Target file path to compare."),
             line_sm: SequenceMatcherName = typer.Option(
                 SequenceMatcherName.HECKEL,
                 help='Choose sequence matching method to detect differences between lines.'),
             inline_sm: SequenceMatcherName = typer.Option(
                 SequenceMatcherName.HECKEL,
                 help='Choose sequence matching method to detect in-line differences between similar lines.'),
             cutoff: float = typer.Option(
                 0.75, min=0.0, max=1.0,
                 help='Line similarity ratio cutoff. If value exceeded then finds in-line differences in similar lines.'
             ),
             char_mode: CharacterMode = typer.Option(
                 CharacterMode.UTF8,
                 help='Character set used when printing diff result.'),
             color_mode: ColorMode = typer.Option(
                 ColorMode.FORE,
                 help='Color mode used when printing diff result.'
             )):
    """
    Reads 2 files from provided paths, compares their content and prints diff.
    If compared lines in text files are similar enough (exceed cutoff) then extracts in-line diff.

    There are few possible strategies to choose to use independently in line-level and in-line-level diff:

        standard: uses built in python SequenceMatcher object to generate diff,
        elements movement detection not supported.

        heckel: detects elements movement in a human-readable form, might not catch all of moves and differences.

        displacement: detects all differences and movements, might not be very useful when both input files contains
        many common lines (for example many empty newlines).
    """
    source = read_file(source_file)
    target = read_file(target_file)
    line_sm_instance = seq_matcher_factory(line_sm.value)()
    inline_sm_instance = seq_matcher_factory(inline_sm.value)()
    console_characters = cli_vis.get_console_characters(char_mode.value)
    console_colors = cli_vis.get_console_colors(color_mode.value)

    a_lines, b_lines, opcodes = diff_lines_with_similarities(
        a=source, b=target, cutoff=cutoff, line_sm=line_sm_instance, inline_sm=inline_sm_instance)

    printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=opcodes,
                                             characters=console_characters,
                                             colors=console_colors, line_margin=3, equal_context=-1)
    printer.print()


def main():
    typer.run(cli_diff)


if __name__ == "__main__":
    main()
