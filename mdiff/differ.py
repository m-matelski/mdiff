from abc import ABC, abstractmethod
import tkinter as tk

from mdiff import diff_lines_with_similarities
from mdiff.seqmatch.utils import SequenceMatcherName, seq_matcher_factory

import mdiff.visualisation.terminal as cli_vis
from mdiff.visualisation.gui_tkinter.diff_result import DiffResult, DiffResultWindowBuilder


class TextDiffer(ABC):
    def __init__(self, a: str, b: str, line_sm: SequenceMatcherName, inline_sm: SequenceMatcherName, cutoff: float,
                 case_sensitive: bool):
        self.a = a
        self.b = b
        self.line_sm = line_sm
        self.inline_sm = inline_sm
        self.cutoff = cutoff
        self.case_sensitive = case_sensitive
        if not 0.0 <= cutoff <= 1.0:
            raise ValueError('cutoff must be in range: 0.0 <= cutoff <= 1.0')

        self.line_sm_instance = seq_matcher_factory(SequenceMatcherName(line_sm))()
        self.inline_sm_instance = seq_matcher_factory(SequenceMatcherName(inline_sm))()

    @abstractmethod
    def run(self):
        pass


class ConsoleTextDiffer(TextDiffer):
    def __init__(self, a: str, b: str, line_sm: SequenceMatcherName, inline_sm: SequenceMatcherName, cutoff: float,
                 case_sensitive: bool, color_mode: str, character_mode: str):
        super().__init__(a, b, line_sm, inline_sm, cutoff, case_sensitive)
        self.color_mode = color_mode
        self.character_mode = character_mode
        self.console_characters = cli_vis.get_console_characters(character_mode)
        self.console_colors = cli_vis.get_console_colors(color_mode)

    def run(self):
        a_lines, b_lines, opcodes = diff_lines_with_similarities(
            a=self.a, b=self.b, cutoff=self.cutoff, line_sm=self.line_sm_instance, inline_sm=self.inline_sm_instance,
            keepends=False, case_sensitive=self.case_sensitive)

        printer = cli_vis.LineDiffConsolePrinter(a=a_lines, b=b_lines, seq=opcodes,
                                                 characters=self.console_characters,
                                                 colors=self.console_colors, line_margin=3, equal_context=-1)
        printer.print()


class TkinterGuiDiffer(TextDiffer):

    def run(self):
        root = tk.Tk()
        root.title('Diff Result')

        diff_result = DiffResult(root)
        window = DiffResultWindowBuilder(root, diff_result)
        diff_result.set_diff_params(a=self.a, b=self.b, line_sm_name=self.line_sm, inline_sm_name=self.inline_sm,
                                    cutoff=self.cutoff, case_sensitive=self.case_sensitive)
        diff_result.generate_diff()
        root.mainloop()
