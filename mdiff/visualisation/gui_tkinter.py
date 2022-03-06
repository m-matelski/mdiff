from enum import Enum
from itertools import zip_longest
from tkinter import ttk
import tkinter as tk
from typing import List, Protocol, Type

from mdiff import OpCode, diff_lines_with_similarities, CompositeOpCode
from mdiff.seqmatch.utils import seq_matcher_factory


class ScrolledText(tk.Text):
    """
    Wraps tkinter Text widget with scrollbars.
    """

    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)

        self.vbar = tk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)

        kw.update({'yscrollcommand': self._yscrollcommand})
        kw.update({'xscrollcommand': self._xscrollcommand})

        tk.Text.__init__(self, self.frame, **kw)

        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vbar['command'] = self.yview
        self.hbar['command'] = self.xview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

        self.on_yscrollcommand = lambda x, y: None
        self.on_xscrollcommand = lambda x, y: None

    def _yscrollcommand(self, first, last):
        self.vbar.set(first, last)
        self.on_yscrollcommand(first, last)

    def _xscrollcommand(self, first, last):
        self.hbar.set(first, last)
        self.on_xscrollcommand(first, last)

    def __str__(self):
        return str(self.frame)


class ResultText(ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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
    text.tag_config(TextDiffTag.INSERT, background="#66ff33")
    text.tag_config(TextDiffTag.DELETE, background="#ff3300")
    text.tag_config(TextDiffTag.MOVE, background="#0099ff")
    text.tag_config(TextDiffTag.MOVED, background="#0099ff")
    text.tag_config(TextDiffTag.REPLACE, background="#cccc00")
    text.tag_config(TextDiffTag.EQUAL, background="")
    text.tag_config(TextDiffTag.IL_INSERT, background="#009900")
    text.tag_config(TextDiffTag.IL_DELETE, background="#ff0000")
    text.tag_config(TextDiffTag.IL_MOVE, background="#0066cc")
    text.tag_config(TextDiffTag.IL_MOVED, background="#0066cc")
    text.tag_config(TextDiffTag.IL_REPLACE, background="#994d00")
    text.tag_config(TextDiffTag.IL_EQUAL, background="#cccc00")


line_opcode_tag_to_text_tag = {
    'insert' :TextDiffTag.INSERT,
    'delete': TextDiffTag.DELETE,
    'move': TextDiffTag.MOVE,
    'moved': TextDiffTag.MOVED,
    'replace': TextDiffTag.REPLACE,
    'equal': TextDiffTag.EQUAL
}

inline_opcode_tag_to_text_tag = {
    'insert' :TextDiffTag.IL_INSERT,
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
    SequenceMatcherChoices.STANDARD: 'standard',
    SequenceMatcherChoices.HECKEL: 'heckel',
    SequenceMatcherChoices.DISPLACEMENT: 'displacement'
}


def get_enum_values(enum: Type[Enum]):
    return [e.value for e in enum]


class DiffResult(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.a = ''
        self.b = ''

        # ---GUI--- left and right text widgets
        self.sql_text_source = ResultText(self, padx=5, pady=2, wrap='none', borderwidth=5)
        self.sql_text_target = ResultText(self, padx=5, pady=2, wrap='none', borderwidth=5)
        # setup text widgets to scroll simultaneously
        self.sql_text_source.on_xscrollcommand = self.on_xscrollcommand_source
        self.sql_text_source.on_yscrollcommand = self.on_yscrollcommand_source
        self.sql_text_target.on_xscrollcommand = self.on_xscrollcommand_target
        self.sql_text_target.on_yscrollcommand = self.on_yscrollcommand_target
        # configure highlight tags
        configure_tags(self.sql_text_source)
        configure_tags(self.sql_text_target)

        # ---GUI--- top frame layout
        self.frame_top = tk.Frame(self)
        self.frame_top.grid(column=0, row=0, sticky='', columnspan=2, padx=3, pady=5)

        # self.frame_top.config(bd=1, relief=tk.SOLID)
        # self.frame_top.grid_columnconfigure(0, weight=1)
        # self.frame_top.grid_columnconfigure(1, weight=1)
        # # self.frame_top.grid_columnconfigure(2, weight=1)
        # # self.frame_top.grid_columnconfigure(3, weight=1)
        # # self.frame_top.grid_columnconfigure(4, weight=1)
        # # self.frame_top.grid_columnconfigure(5, weight=1)
        # self.frame_top.grid_rowconfigure(0, weight=1)

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

        # ---GUI--- generate
        self.button_generate = tk.Button(self.frame_top, text='Generate Diff', command=self.generate_diff)
        self.button_generate.grid(column=4, row=0, sticky='nw', padx=10)

        # ---GUI--- grid and layout settings
        # self.pw_text = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        # self.pw_text.add(self.sql_text_source, stretch="always")
        # self.pw_text.add(self.sql_text_target, stretch="always")
        # self.pw_text.grid(column=0, row=1, sticky='nsew', columnspan=2, padx=3, pady=5)

        self.sql_text_source.grid(column=0, row=1, sticky='nsew')
        self.sql_text_target.grid(column=1, row=1, sticky='nsew')
        #
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=10000)
        self.grid_rowconfigure(0, weight=1)

        # self.load_comparison_result()
        # TODO: run diff on init with default settings
        # TODO: button to rerun diff (no auto run)
        # TODO: sort by
        # TODO: swap texts

    def set_a(self, a):
        self.a = a

    def set_b(self, b):
        self.b = b

    def generate_diff(self):
        self.set_text_state('normal')
        self.text_clear()

        a = self.a
        b = self.b
        cutoff = self.scale_cutoff_value.get()
        line_sm = seq_matcher_factory(sm_choice_to_factory_name[self.combo_line_sm.get()])()
        inline_sm = seq_matcher_factory(sm_choice_to_factory_name[self.combo_in_line_sm.get()])()
        a_lines, b_lines, opcodes = diff_lines_with_similarities(
            a=a, b=b, cutoff=cutoff, line_sm=line_sm, inline_sm=inline_sm, keepends=True)

        a_line_off = b_line_off = 0
        for opcode in opcodes:
            tag, i1, i2, j1, j2 = opcode
            left_len = i2-i1
            right_len = j2-j1
            max_len = max(left_len, right_len)

            if tag == 'replace':
                if isinstance(opcode, CompositeOpCode) and opcode.children_opcodes:
                    for inline_opcode in opcode.children_opcodes:
                        il_tag, il_i1, il_i2, il_j1, il_j2 = inline_opcode
                        il_text_tag = inline_opcode_tag_to_text_tag[il_tag].value
                        print(f'printing on source: {a_lines[i1][il_i1:il_i2]} with tag {il_text_tag}')
                        print(f'printing on target: {b_lines[j1][il_j1:il_j2]} with tag {il_text_tag}')
                        self.sql_text_source.insert('end', a_lines[i1][il_i1:il_i2], (il_text_tag,))
                        self.sql_text_target.insert('end', b_lines[j1][il_j1:il_j2], (il_text_tag,))
                    continue

                else:
                    delete_tag = line_opcode_tag_to_text_tag['delete'].value
                    insert_tag = line_opcode_tag_to_text_tag['insert'].value
                    left_tags = [delete_tag] * left_len + [None] * (max_len - left_len)
                    right_tags = [insert_tag] * right_len + [None] * (max_len - right_len)
            else:
                text_tag = line_opcode_tag_to_text_tag[tag].value
                left_tags = [text_tag]*left_len + [None]*(max_len-left_len)
                right_tags = [text_tag]*right_len + [None]*(max_len-right_len)

            for left_line, right_line, left_text_tag, right_text_tag in \
                    zip_longest(a_lines[i1:i2], b_lines[j1:j2], left_tags, right_tags, fillvalue='\n'):
                self.sql_text_source.insert('end', left_line, (left_text_tag,))
                self.sql_text_target.insert('end', right_line, (right_text_tag,))


        self.set_text_state('disabled')



    def on_option_change(self):
        print('on_option_change')

    def sort_by_selection(self, event=None):
        self.combo_sort_by.selection_clear()
        # self.load_comparison_result()

    def line_sm_selection(self, event=None):
        pass

    def in_line_sm_selection(self, event=None):
        pass

    # def load_comparison_result(self):
    #
    #     self.set_sql_text_state('normal')
    #     self.sql_text_clear()
    #     diff_mode = self.combo_diff_mode.get()
    #
    #
    #     comparison_result = self.comparison_result
    #     if diff_mode==self.DIFF_MODE_SOURCE:
    #         comparison_result = self.comparison_result.order_by_source()
    #     elif diff_mode==self.DIFF_MODE_TARGET:
    #         comparison_result = self.comparison_result.order_by_target()
    #
    #     # print(self.comparison_result)
    #     # for i in range(100):
    #     #     self.sql_text_source.insert(tk.END, f"field{i} DECIMAL(15,5)\n")
    #     #     self.sql_text_target.insert(tk.END, f"field{i} DECIMAL(15,5)\n")
    #     for cr in comparison_result:
    #         src_verse = (str(cr.key.source) if cr.key.source else '') + '\n'
    #         tgt_verse = (str(cr.key.target) if cr.key.target else '') + '\n'
    #         self.sql_text_source.insert('end', src_verse)
    #         self.sql_text_target.insert('end', tgt_verse)
    #
    #     for i in (self.sql_text_source, self.sql_text_target):
    #         i.put_styled_text()
    #
    #     # set backgrounds
    #     # self.sql_text_source.tag_add('warning', '1.2', '5.0')
    #     for i, cr in enumerate(comparison_result, start=1):
    #         start = str(i) + '.0'
    #         end = str(i+1) + '.0'
    #         tag = self.get_tag(cr)
    #         self.sql_text_source.tag_add(tag, start, end)
    #         self.sql_text_target.tag_add(tag, start, end)
    #
    #     self.set_sql_text_state('disabled')

    # def get_tag(self, result: KeyColumnComparisonResult):
    #     type_match = result.type_name_match and result.precision_match and result.sacle_match
    #     if result.key.match and result.key.order_match and type_match:
    #         return self.TAG_DIFF_MATCH
    #     elif result.key.match and not result.key.order_match and type_match:
    #         return self.TAG_DIFF_ORDER_DONT_MATCH
    #     elif result.key.match and result.key.order_match and not type_match:
    #         return self.TAG_DIFF_TYPE_DONT_MATCH
    #     elif result.key.match and not result.key.order_match and not type_match:
    #         print('nomatch order')
    #         return self.TAG_DIFF_NO_MATCH_AND_ORDER
    #     elif not result.key.match:
    #         print('dontexists')
    #         return self.TAG_DIFF_TYPE_DONT_EXIST
    #     return ''

    def text_clear(self):
        for i in (self.sql_text_source, self.sql_text_target):
            i.delete('1.0', tk.END)

    def set_text_state(self, state):
        for i in (self.sql_text_source, self.sql_text_target):
            # i.put_styled_text()
            i.configure(state=state)

    def on_yscrollcommand_source(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.sql_text_source.yview()
            self.sql_text_target.yview_moveto(view_pos[0])

    def on_xscrollcommand_source(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.sql_text_source.xview()
            self.sql_text_target.xview_moveto(view_pos[0])

    def on_yscrollcommand_target(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.sql_text_target.yview()
            self.sql_text_source.yview_moveto(view_pos[0])

    def on_xscrollcommand_target(self, first, last):
        if not self.has_text_scrollbars_the_same_position():
            view_pos = self.sql_text_target.xview()
            self.sql_text_source.xview_moveto(view_pos[0])

    def has_text_scrollbars_the_same_position(self):
        return self.sql_text_source.hbar.get() == self.sql_text_target.hbar.get() and \
               self.sql_text_source.vbar.get() == self.sql_text_target.vbar.get()


class DiffResult2(tk.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.text_a = tk.Text(self)
        self.text_b = tk.Text(self)

        self.text_a.grid(column=0, row=0, sticky='nesw')
        self.text_b.grid(column=1, row=0, sticky='nesw')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
