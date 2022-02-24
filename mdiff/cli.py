from pathlib import Path
from typing import Literal

import typer

from mdiff.seqmatch.utils import seq_matcher_factory
from mdiff.text_diff import diff_lines_with_similarities
import mdiff.visualisation.terminal as cli_vis
from mdiff.utils import read_file

sm_valid_names = ('standard', 'heckel', 'displacement')


def cli_diff(source_file: Path, target_file: Path,
             line_sm_name: str = 'heckel',
             similarities_sm_name: str = 'standard',
             cutoff: float = 0.75,
             char_mode: str = 'utf8',
             color_mode: str = 'fore'
             ):
    """
    docs
    """
    source = read_file(source_file)
    target = read_file(target_file)
    line_sm = seq_matcher_factory(line_sm_name)()
    similarities_sm = seq_matcher_factory(similarities_sm_name)()
    console_characters = cli_vis.get_console_characters(char_mode)
    console_colors = cli_vis.get_console_colors(color_mode)

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
