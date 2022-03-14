from pathlib import Path

import typer

from mdiff.differ import ConsoleTextDiffer, TkinterGuiDiffer
from mdiff.utils import read_file, StringEnumChoice

sm_valid_names = ('standard', 'heckel', 'displacement')


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
             gui: bool = typer.Option(False, help='Open GUI window with diff result.'),
             case_sensitive: bool = typer.Option(True, help='Whether diff is going to be case sensitive.'),
             char_mode: CharacterMode = typer.Option(
                 CharacterMode.UTF8,
                 help='Terminal character set used when printing diff result.'),
             color_mode: ColorMode = typer.Option(
                 ColorMode.FORE,
                 help='Terminal color mode used when printing diff result.'
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
    if not gui:
        differ = ConsoleTextDiffer(a=source, b=target, line_sm=line_sm, inline_sm=inline_sm, cutoff=cutoff,
                                   color_mode=color_mode.value, character_mode=char_mode.value,
                                   case_sensitive=case_sensitive)
        differ.run()
    else:
        differ = TkinterGuiDiffer(a=source, b=target, line_sm=line_sm, inline_sm=inline_sm, cutoff=cutoff,
                                  case_sensitive=case_sensitive)
        differ.run()


def main():
    typer.run(cli_diff)


if __name__ == "__main__":
    main()
