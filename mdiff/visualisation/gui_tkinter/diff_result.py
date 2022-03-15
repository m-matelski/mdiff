import tkinter as tk
from enum import Enum
from itertools import zip_longest
from tkinter import ttk
from typing import Protocol, Union

from mdiff import diff_lines_with_similarities, CompositeOpCode
from mdiff.seqmatch.utils import SequenceMatcherName, seq_matcher_factory
from mdiff.utils import CompositeDelegationMixin, get_enum_values, sort_seq_by_other_seq, sort_string_seq, \
    sort_string_seq_by_other
from mdiff.visualisation.gui_tkinter.utils import ScrolledText, WindowBuilder


# Defining tags, colors and mappings for coloring background in Text widgets using diff result data
class TextDiffTag(str, Enum):
    INSERT = 'INSERT'
    DELETE = 'DELETE'
    MOVE = 'MOVE'
    MOVED = 'MOVED'
    REPLACE = 'REPLACE'
    EQUAL = 'EQUAL'
    IL_INSERT = 'IL_INSERT'
    IL_DELETE = 'IL_DELETE'
    IL_MOVE = 'IL_MOVE'
    IL_MOVED = 'IL_MOVED'
    IL_REPLACE = 'IL_REPLACE'
    IL_EQUAL = 'IL_EQUAL'


class TagConfigurator(Protocol):
    def __call__(self, text: tk.Text) -> None: ...


def configure_tags(text: tk.Text):
    text.tag_config(TextDiffTag.INSERT, background="#99ff99")
    text.tag_config(TextDiffTag.DELETE, background="#ff9999")
    text.tag_config(TextDiffTag.MOVE, background="#b3e6ff")
    text.tag_config(TextDiffTag.MOVED, background="#b3e6ff")
    text.tag_config(TextDiffTag.REPLACE, background="#ffd699")
    text.tag_config(TextDiffTag.EQUAL, background="")
    text.tag_config(TextDiffTag.IL_INSERT, background="#66ff66")
    text.tag_config(TextDiffTag.IL_DELETE, background="#ff6666")
    text.tag_config(TextDiffTag.IL_MOVE, background="#80d4ff")
    text.tag_config(TextDiffTag.IL_MOVED, background="#80d4ff")
    text.tag_config(TextDiffTag.IL_REPLACE, background="#ffad33")
    text.tag_config(TextDiffTag.IL_EQUAL, background="#ffd699")


line_opcode_tag_to_text_tag = {
    'insert': TextDiffTag.INSERT,
    'delete': TextDiffTag.DELETE,
    'move': TextDiffTag.MOVE,
    'moved': TextDiffTag.MOVED,
    'replace': TextDiffTag.REPLACE,
    'equal': TextDiffTag.EQUAL
}
inline_opcode_tag_to_text_tag = {
    'insert': TextDiffTag.IL_INSERT,
    'delete': TextDiffTag.IL_DELETE,
    'move': TextDiffTag.IL_MOVE,
    'moved': TextDiffTag.IL_MOVED,
    'replace': TextDiffTag.IL_REPLACE,
    'equal': TextDiffTag.IL_EQUAL
}


class SortChoices(str, Enum):
    NO = 'No'
    BY_SOURCE = 'By source'
    BY_TARGET = 'By target'
    YES = 'Yes'


class SequenceMatcherChoices(str, Enum):
    STANDARD = 'Standard'
    HECKEL = 'Heckel'
    DISPLACEMENT = 'Displacement'


sm_choice_to_factory_name = {
    SequenceMatcherChoices.STANDARD: SequenceMatcherName.STANDARD,
    SequenceMatcherChoices.HECKEL: SequenceMatcherName.HECKEL,
    SequenceMatcherChoices.DISPLACEMENT: SequenceMatcherName.DISPLACEMENT
}
factory_name_to_sm_choice = {v: k for k, v in sm_choice_to_factory_name.items()}


class ResultText(ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TextComposite(tk.Text, CompositeDelegationMixin):
    """Allows to treat group of Text widgets as one component."""

    def __init__(self, **kw):
        CompositeDelegationMixin.__init__(self)
        super().__init__()


class DiffResult(tk.Frame):
    """
    Main diff result frame containing two Text widgets side by side for presenting diff result.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.a = ''
        self.b = ''

        self.frame_bottom = tk.Frame(self)
        self.frame_bottom.grid(column=0, row=1, sticky='nsew', padx=3, pady=1)
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.rowconfigure(0, weight=1)
        # ---GUI--- left and right text widgets
        self.text_source = ResultText(self.frame_bottom, padx=5, pady=2, wrap='none', borderwidth=5)
        self.text_target = ResultText(self.frame_bottom, padx=5, pady=2, wrap='none', borderwidth=5)
        self.texts = TextComposite()
        self.texts.__children__.extend([self.text_source, self.text_target])
        configure_tags(self.texts)
        self.texts.tag_raise('sel')
        # setup text widgets to scroll simultaneously
        self.text_source.on_xscrollcommand = self.on_xscrollcommand_source
        self.text_source.on_yscrollcommand = self.on_yscrollcommand_source
        self.text_target.on_xscrollcommand = self.on_xscrollcommand_target
        self.text_target.on_yscrollcommand = self.on_yscrollcommand_target

        # ---GUI--- top frame layout
        self.frame_top = tk.Frame(self)
        self.frame_top.grid(column=0, row=0, sticky='', padx=3, pady=1)

        # ---GUI--- line level sequence matcher: label + combobox
        self.frame_line_sm = tk.Frame(self.frame_top)
        self.frame_line_sm.grid(column=0, row=0, sticky='nw', padx=10)
        self.lbl_line_sm = tk.Label(self.frame_line_sm, text='Line SM:')
        self.lbl_line_sm.grid(column=0, row=0, sticky='nw')
        self.combo_line_sm = ttk.Combobox(self.frame_line_sm)
        self.combo_line_sm['values'] = get_enum_values(SequenceMatcherChoices)
        self.combo_line_sm.state(['readonly'])
        self.combo_line_sm.bind('<<ComboboxSelected>>', self.line_sm_selection)
        self.combo_line_sm.grid(column=1, row=0, sticky='nw')
        self.combo_line_sm.current(1)

        # ---GUI--- in-line level sequence matcher: label + combobox
        self.frame_in_line_sm = tk.Frame(self.frame_top)
        self.frame_in_line_sm.grid(column=1, row=0, sticky='nw', padx=10)
        self.lbl_in_line_sm = tk.Label(self.frame_in_line_sm, text='Line SM:')
        self.lbl_in_line_sm.grid(column=0, row=0, sticky='nw')
        self.combo_in_line_sm = ttk.Combobox(self.frame_in_line_sm)
        self.combo_in_line_sm['values'] = get_enum_values(SequenceMatcherChoices)
        self.combo_in_line_sm.state(['readonly'])
        self.combo_in_line_sm.bind('<<ComboboxSelected>>', self.in_line_sm_selection)
        self.combo_in_line_sm.grid(column=1, row=0, sticky='nw')
        self.combo_in_line_sm.current(1)

        # ---GUI--- cutoff label + slider
        self.frame_cutoff = tk.Frame(self.frame_top)
        self.frame_cutoff.grid(column=2, row=0, sticky='nw', padx=10)
        self.lbl_cutoff = tk.Label(self.frame_cutoff, text='Cutoff:')
        self.lbl_cutoff.grid(column=0, row=0, sticky='nw')
        self.scale_cutoff_value = tk.DoubleVar()
        self.scale_cutoff = tk.Scale(self.frame_cutoff, orient=tk.HORIZONTAL, length=200, from_=0.0, to=1.0,
                                     resolution=0.01, showvalue=False, variable=self.scale_cutoff_value)
        self.scale_cutoff.set(0.75)
        self.scale_cutoff.grid(column=1, row=0, sticky='nw')
        self.lbl_cutoff_value = tk.Label(self.frame_cutoff, textvariable=self.scale_cutoff_value)
        self.lbl_cutoff_value.grid(column=2, row=0, sticky='nw')

        # ---GUI--- sort by: label + combobox
        self.frame_sort_by = tk.Frame(self.frame_top)
        self.frame_sort_by.grid(column=3, row=0, sticky='nw', padx=10)
        self.lbl_sort_by = tk.Label(self.frame_sort_by, text='Sort content:')
        self.lbl_sort_by.grid(column=0, row=0, sticky='nw')
        self.combo_sort_by = ttk.Combobox(self.frame_sort_by)
        self.combo_sort_by['values'] = get_enum_values(SortChoices)
        self.combo_sort_by.state(['readonly'])
        self.combo_sort_by.bind('<<ComboboxSelected>>', self.sort_by_selection)
        self.combo_sort_by.grid(column=1, row=0, sticky='nw')
        self.combo_sort_by.current(0)

        # ---GUI
        self.case_sensitive = tk.BooleanVar(value=True)
        self.check_case_sensitive = tk.Checkbutton(self.frame_top, text='Case sensitive', variable=self.case_sensitive)
        self.check_case_sensitive.grid(column=4, row=0, sticky='nw', padx=10)

        # ---GUI--- generate
        self.button_generate = tk.Button(self.frame_top, text='Generate Diff', command=self.generate_diff)
        self.button_generate.grid(column=5, row=0, sticky='nw', padx=10)

        self.text_source.grid(column=0, row=0, sticky='nsew')
        self.text_target.grid(column=1, row=0, sticky='nsew')
        #
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10000)
        self.grid_rowconfigure(0, weight=1)

    def set_a(self, a: str):
        """Set source text"""
        self.a = a

    def set_b(self, b: str):
        """Set target text"""
        self.b = b

    def set_diff_params(self, a: str, b: str,
                        line_sm_name: SequenceMatcherName = SequenceMatcherName.HECKEL,
                        inline_sm_name: SequenceMatcherName = SequenceMatcherName.HECKEL,
                        cutoff: float = 0.75, case_sensitive: bool = False):
        """
        Set diff parameters for a widget
        """
        if not 0.0 <= cutoff <= 1.0:
            raise ValueError('cutoff must be in range: 0.0 <= cutoff <= 1.0')
        self.scale_cutoff_value.set(cutoff)
        self.a = a
        self.b = b
        self.combo_line_sm.set(factory_name_to_sm_choice[line_sm_name.value])
        self.combo_in_line_sm.set(factory_name_to_sm_choice[inline_sm_name.value])
        self.case_sensitive.set(value=case_sensitive)

    def handle_sort(self):
        """Sort source and target text lines"""
        a_lines = self.a.splitlines(keepends=False)
        b_lines = self.b.splitlines(keepends=False)
        option = SortChoices(self.combo_sort_by.get())
        case_sensitive = self.case_sensitive.get()
        if option == SortChoices.NO:
            return self.a, self.b
        elif option == SortChoices.YES:
            return '\n'.join(sort_string_seq(a_lines, case_sensitive)), \
                   '\n'.join(sort_string_seq(a_lines, case_sensitive))
        elif option == SortChoices.BY_SOURCE:
            return self.a, '\n'.join(sort_string_seq_by_other(b_lines, a_lines, case_sensitive))
        elif option == SortChoices.BY_TARGET:
            return '\n'.join(sort_string_seq_by_other(a_lines, b_lines, case_sensitive)), self.b

    def generate_diff(self):
        """
        Takes parameters info from widgets and generates diff for intput texts.
        """
        src_yview = self.text_source.yview()
        tgt_yview = self.text_target.yview()
        self.texts.configure(state='normal')
        self.texts.delete('1.0', tk.END)

        a, b = self.handle_sort()
        cutoff = self.scale_cutoff_value.get()
        line_sm = seq_matcher_factory(sm_choice_to_factory_name[self.combo_line_sm.get()])()
        inline_sm = seq_matcher_factory(sm_choice_to_factory_name[self.combo_in_line_sm.get()])()
        a_lines, b_lines, opcodes = diff_lines_with_similarities(
            a=a, b=b, cutoff=cutoff, line_sm=line_sm, inline_sm=inline_sm, keepends=True,
            case_sensitive=self.case_sensitive.get())

        for opcode in opcodes:
            tag, i1, i2, j1, j2 = opcode
            left_len = i2 - i1
            right_len = j2 - j1
            max_len = max(left_len, right_len)

            if tag == 'replace':
                if isinstance(opcode, CompositeOpCode) and opcode.children_opcodes:
                    for inline_opcode in opcode.children_opcodes:
                        il_tag, il_i1, il_i2, il_j1, il_j2 = inline_opcode
                        il_text_tag = inline_opcode_tag_to_text_tag[il_tag].value
                        self.text_source.insert('end', a_lines[i1][il_i1:il_i2], (il_text_tag,))
                        self.text_target.insert('end', b_lines[j1][il_j1:il_j2], (il_text_tag,))
                    continue

                else:
                    delete_tag = line_opcode_tag_to_text_tag['delete'].value
                    insert_tag = line_opcode_tag_to_text_tag['insert'].value
                    left_tags = [delete_tag] * left_len + [None] * (max_len - left_len)
                    right_tags = [insert_tag] * right_len + [None] * (max_len - right_len)
            else:
                text_tag = line_opcode_tag_to_text_tag[tag].value
                left_tags = [text_tag] * left_len + [None] * (max_len - left_len)
                right_tags = [text_tag] * right_len + [None] * (max_len - right_len)

            for left_line, right_line, left_text_tag, right_text_tag in \
                    zip_longest(a_lines[i1:i2], b_lines[j1:j2], left_tags, right_tags, fillvalue='\n'):
                self.text_source.insert('end', left_line, (left_text_tag,))
                self.text_target.insert('end', right_line, (right_text_tag,))

        self.texts.configure(state='disabled')
        self.text_source.yview_moveto(src_yview[0])
        self.text_target.yview_moveto(tgt_yview[0])

    def sort_by_selection(self, event=None):
        """Triggered on Sort By: combo box selection"""
        pass

    def line_sm_selection(self, event=None):
        """Triggered on Line SM: combo box selection"""
        pass

    def in_line_sm_selection(self, event=None):
        """Triggered on InLine SM: combo box selection"""
        pass

    def on_yscrollcommand_source(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.text_source.yview()
            self.text_target.yview_moveto(view_pos[0])

    def on_xscrollcommand_source(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.text_source.xview()
            self.text_target.xview_moveto(view_pos[0])

    def on_yscrollcommand_target(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.text_target.yview()
            self.text_source.yview_moveto(view_pos[0])

    def on_xscrollcommand_target(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.text_target.xview()
            self.text_source.xview_moveto(view_pos[0])

    def has_text_scrollbars_the_same_position(self):
        return self.text_source.hbar.get() == self.text_target.hbar.get() and \
               self.text_source.vbar.get() == self.text_target.vbar.get()


class DiffResultWindowBuilder(WindowBuilder):
    """
    Builds Diff Result window. It takes Tk or TopLevel window class as parent window, and content frame
    (DiffResult) as parameters.

    Reason for wrapping is that Diff Result is sub window (TopLevel window) in main GUI application, but it's
    main window (Tk - root window) if called from CLI. It allows to reduce code duplication if the same window
    settings are used for both Tk and TopLevel.
    """

    def __init__(self, window: Union[tk.Tk, tk.Toplevel], content: tk.Frame):
        super().__init__(window, content)
        self.content.grid(column=0, row=0, sticky='nsew')
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        self.window.option_add('*tearOff', tk.FALSE)
        self.menu_bar = tk.Menu(self.window)
        self.window['menu'] = self.menu_bar

        self.menu_file = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_file, label='File', underline=0)
        self.menu_file.add_command(label='Close', command=lambda: self.window.destroy())

        self.menu_edit = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_edit, label='Edit', underline=0)
        self.menu_edit.add_command(label='Copy', accelerator='Ctrl+C',
                                   command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
