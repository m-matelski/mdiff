from enum import Enum
from pathlib import Path

import typer

from mdiff.seqmatch.utils import seq_matcher_factory
from mdiff.text_diff import diff_lines_with_similarities
import mdiff.visualisation.terminal as cli_vis
from mdiff.utils import read_file

sm_valid_names = ('standard', 'heckel', 'displacement')


class SequenceMatcherName(str, Enum):
    STANDARD = 'standard'
    HECKEL = 'heckel'


class CharacterMode(str, Enum):
    UTF8 = 'utf8'
    ASCII = 'ascii'


class ColorMode(str, Enum):
    FORE = 'fore'
    BACK = 'back'


def cli_diff(source_file: Path = typer.Argument(..., help="Source file path to compare."),
             target_file: Path = typer.Argument(..., help="Target file path to compare."),
             line_sm_name: SequenceMatcherName = typer.Option(
                 SequenceMatcherName.HECKEL,
                 help='Choose sequence matching method to detect differences between lines.'),
             similarities_sm_name: SequenceMatcherName = typer.Option(
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
    """
    source = read_file(source_file)
    target = read_file(target_file)
    line_sm = seq_matcher_factory(line_sm_name.value)()
    similarities_sm = seq_matcher_factory(similarities_sm_name.value)()
    console_characters = cli_vis.get_console_characters(char_mode.value)
    console_colors = cli_vis.get_console_colors(color_mode.value)

    a_lines, b_lines, opcodes = diff_lines_with_similarities(
        a=source, b=target, line_similarity_cutoff=cutoff, line_sm=line_sm, similarities_sm=similarities_sm)

    printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=opcodes,
                                             characters=console_characters,
                                             colors=console_colors, line_margin=3, equal_context=-1)
    printer.print()


def main():
    typer.run(cli_diff)


if __name__ == "__main__":
    main()
