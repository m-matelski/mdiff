# # nothing interesting here, just some old code as reference
#
# from tkinter import ttk
# import tkinter as tk
#
# class ScrolledText(tk.Text):
#     def __init__(self, master=None, **kw):
#         self.frame = tk.Frame(master)
#
#         self.vbar = tk.Scrollbar(self.frame)
#         self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#         self.hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
#         self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
#
#         kw.update({'yscrollcommand': self._yscrollcommand})
#         kw.update({'xscrollcommand': self._xscrollcommand})
#
#
#         tk.Text.__init__(self, self.frame, **kw)
#
#         self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
#         self.vbar['command'] = self.yview
#         self.hbar['command'] = self.xview
#
#         # Copy geometry methods of self.frame without overriding Text
#         # methods -- hack!
#         text_meths = vars(tk.Text).keys()
#         methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
#         methods = methods.difference(text_meths)
#
#         for m in methods:
#             if m[0] != '_' and m != 'config' and m != 'configure':
#                 setattr(self, m, getattr(self.frame, m))
#
#         self.on_yscrollcommand = lambda x, y: None
#         self.on_xscrollcommand = lambda x, y: None
#
#
#     def _yscrollcommand(self, first, last):
#         self.vbar.set(first, last)
#         self.on_yscrollcommand(first, last)
#
#     def _xscrollcommand(self, first, last):
#         self.hbar.set(first, last)
#         self.on_xscrollcommand(first, last)
#
#     def __str__(self):
#         return str(self.frame)
#
#
# class ResultText(ScrolledText):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
#
#
# class SqlDiffResult(tk.Toplevel):
#
#     TAG_DIFF_MATCH = 'TAG_DIFF_MATCH'
#     TAG_DIFF_ORDER_DONT_MATCH = 'TAG_DIFF_ORDER_DONT_MATCH'
#     TAG_DIFF_TYPE_DONT_MATCH = 'TAG_DIFF_TYPE_DONT_MATCH'
#     TAG_DIFF_NO_MATCH_AND_ORDER = 'TAG_DIFF_NO_MATCH_AND_ORDER'
#     TAG_DIFF_TYPE_DONT_EXIST = 'TAG_DIFF_TYPE_DONT_EXIST'
#
#     DIFF_MODE_BOTH = 'Source/Target'
#     DIFF_MODE_SOURCE = 'Source'
#     DIFF_MODE_TARGET = 'Target'
#     DIFF_MODES = (DIFF_MODE_BOTH, DIFF_MODE_SOURCE, DIFF_MODE_TARGET)
#
#
#     def __init__(self, a, b, opcodes, *args, **kwargs):
#         # Window
#         super().__init__(*args, **kwargs)
#
#         self.a = a
#         self.b = b
#         self.opcodes = opcodes
#
#         self.text_a = ResultText(self, padx=5, pady=2, wrap='none')
#         self.text_b = ResultText(self, padx=5, pady=2, wrap='none')
#         self.text_a.on_xscrollcommand = self.on_xscrollcommand_source
#         self.text_a.on_yscrollcommand = self.on_yscrollcommand_source
#         self.text_b.on_xscrollcommand = self.on_xscrollcommand_target
#         self.text_b.on_yscrollcommand = self.on_yscrollcommand_target
#
#         for sql_text in (self.text_a, self.text_b):
#             sql_text.tag_config(self.TAG_DIFF_MATCH, background="#adffc3")
#             sql_text.tag_config(self.TAG_DIFF_ORDER_DONT_MATCH, background="#abe7ff")
#             sql_text.tag_config(self.TAG_DIFF_TYPE_DONT_MATCH, background="#fffbc4")
#             sql_text.tag_config(self.TAG_DIFF_NO_MATCH_AND_ORDER, background="#ffb7dd")
#             sql_text.tag_config(self.TAG_DIFF_TYPE_DONT_EXIST, background="#ff9a9a")
#
#         self.frame_top = tk.Frame(self)
#         self.frame_top.grid(column=0, row=0, sticky='', columnspan=2, padx=3, pady=3)
#         # self.frame_top.config(bd=1, relief=tk.SOLID)
#         self.frame_top.grid_columnconfigure(0, weight=1)
#         self.frame_top.grid_columnconfigure(1, weight=1)
#         self.frame_top.grid_rowconfigure(0, weight=1)
#
#         # self.lbl_diff_mode = tk.Label(self.frame_top, text='Diff mode:')
#         # self.lbl_diff_mode.grid(column=0, row=0, sticky='nw', padx=5)
#
#         # self.combo_diff_mode = ttk.Combobox(self.frame_top)
#         # self.combo_diff_mode['values'] = self.DIFF_MODES
#         # self.combo_diff_mode.state(['readonly'])
#         # self.combo_diff_mode.bind('<<ComboboxSelected>>', self.diff_mode_selection)
#         # self.combo_diff_mode.grid(column=1, row=0, sticky='nw')
#         # self.combo_diff_mode.current(0)
#
#         self.text_a.grid(column=0, row=1, sticky='nwes')
#         self.text_b.grid(column=1, row=1, sticky='nwes')
#
#         self.grid_columnconfigure(0, weight=1)
#         self.grid_columnconfigure(1, weight=1)
#         self.grid_rowconfigure(1, weight=10000)
#         self.grid_rowconfigure(0, weight=1)
#
#         self.load_comparison_result()
#
#     # def diff_mode_selection(self, event=None):
#     #     self.combo_diff_mode.selection_clear()
#     #     self.load_comparison_result()
#
#     def load_comparison_result(self):
#
#         self.set_sql_text_state('normal')
#         self.sql_text_clear()
#         diff_mode = self.combo_diff_mode.get()
#
#
#         comparison_result = self.comparison_result
#         if diff_mode==self.DIFF_MODE_SOURCE:
#             comparison_result = self.comparison_result.order_by_source()
#         elif diff_mode==self.DIFF_MODE_TARGET:
#             comparison_result = self.comparison_result.order_by_target()
#
#         # print(self.comparison_result)
#         # for i in range(100):
#         #     self.sql_text_source.insert(tk.END, f"field{i} DECIMAL(15,5)\n")
#         #     self.sql_text_target.insert(tk.END, f"field{i} DECIMAL(15,5)\n")
#         for cr in comparison_result:
#             src_verse = (str(cr.key.source) if cr.key.source else '') + '\n'
#             tgt_verse = (str(cr.key.target) if cr.key.target else '') + '\n'
#             self.text_a.insert('end', src_verse)
#             self.text_b.insert('end', tgt_verse)
#
#         for i in (self.text_a, self.text_b):
#             i.put_styled_text()
#
#         # set backgrounds
#         # self.sql_text_source.tag_add('warning', '1.2', '5.0')
#         for i, cr in enumerate(comparison_result, start=1):
#             start = str(i) + '.0'
#             end = str(i+1) + '.0'
#             tag = self.get_tag(cr)
#             self.text_a.tag_add(tag, start, end)
#             self.text_b.tag_add(tag, start, end)
#
#         self.set_sql_text_state('disabled')
#
#     def get_tag(self, result: KeyColumnComparisonResult):
#         type_match = result.type_name_match and result.precision_match and result.sacle_match
#         if result.key.match and result.key.order_match and type_match:
#             return self.TAG_DIFF_MATCH
#         elif result.key.match and not result.key.order_match and type_match:
#             return self.TAG_DIFF_ORDER_DONT_MATCH
#         elif result.key.match and result.key.order_match and not type_match:
#             return self.TAG_DIFF_TYPE_DONT_MATCH
#         elif result.key.match and not result.key.order_match and not type_match:
#             print('nomatch order')
#             return self.TAG_DIFF_NO_MATCH_AND_ORDER
#         elif not result.key.match:
#             print('dontexists')
#             return self.TAG_DIFF_TYPE_DONT_EXIST
#         return ''
#
#     def sql_text_clear(self):
#         for i in (self.text_a, self.text_b):
#             i.delete('1.0', tk.END)
#
#     def set_sql_text_state(self, state):
#         for i in (self.text_a, self.text_b):
#             # i.put_styled_text()
#             i.configure(state=state)
#
#     def on_yscrollcommand_source(self, first, last):
#         if not self.has_text_scrollbars_the_same_position():
#             view_pos = self.text_a.yview()
#             self.text_b.yview_moveto(view_pos[0])
#
#     def on_xscrollcommand_source(self, first, last):
#         if not self.has_text_scrollbars_the_same_position():
#             view_pos = self.text_a.xview()
#             self.text_b.xview_moveto(view_pos[0])
#
#     def on_yscrollcommand_target(self, first, last):
#         if not self.has_text_scrollbars_the_same_position():
#             view_pos = self.text_b.yview()
#             self.text_a.yview_moveto(view_pos[0])
#
#     def on_xscrollcommand_target(self, first, last):
#         if not self.has_text_scrollbars_the_same_position():
#             view_pos = self.text_b.xview()
#             self.text_a.xview_moveto(view_pos[0])
#
#     def has_text_scrollbars_the_same_position(self):
#         return self.text_a.hbar.get() == self.text_b.hbar.get() and \
#                self.text_a.vbar.get() == self.text_b.vbar.get()
