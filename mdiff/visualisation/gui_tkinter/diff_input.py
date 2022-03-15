import tkinter as tk
from typing import Union

from mdiff.visualisation.gui_tkinter.diff_result import DiffResultWindowBuilder, DiffResult
from mdiff.visualisation.gui_tkinter.utils import ScrolledText


def maximize_window(window: Union[tk.Tk, tk.Toplevel]):
    try:
        window.state('zoomed')
        return
    except tk.TclError:
        pass

    try:
        window.attributes('-zoomed', True)
        return
    except tk.TclError:
        pass


class DiffInputWindow(tk.Tk):
    """
    Main GUI window with 2 text inputs used to generate diff.
    """

    def __init__(self):
        super().__init__()

        self.title('mdiff')
        maximize_window(self)

        # widgets
        self.frame_text = tk.Frame(self)
        self.frame_text.grid(column=0, row=0, sticky='nsew', padx=0, pady=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.text_source = ScrolledText(self.frame_text)
        self.text_target = ScrolledText(self.frame_text)
        self.text_source.grid(column=0, row=0, sticky='nsew', padx=3, pady=3)
        self.text_target.grid(column=1, row=0, sticky='nsew', padx=3, pady=3)
        self.frame_text.columnconfigure(0, weight=1)
        self.frame_text.columnconfigure(1, weight=1)
        self.frame_text.rowconfigure(0, weight=1)

        # menu bar
        self.option_add('*tearOff', tk.FALSE)
        self.menu_bar = tk.Menu(self)
        self['menu'] = self.menu_bar

        self.menu_file = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_file, label='File', underline=0)
        self.menu_file.add_command(label='Close', command=lambda: self.destroy())

        self.menu_edit = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_edit, label='Edit', underline=0)
        self.menu_edit.add_command(label='Copy', accelerator='Ctrl+C',
                                   command=lambda: self.focus_get().event_generate("<<Copy>>"))
        self.menu_edit.add_command(label='Cut', accelerator='Ctrl+X',
                                   command=lambda: self.focus_get().event_generate("<<Cut>>"))
        self.menu_edit.add_command(label='Paste', accelerator='Ctrl+V',
                                   command=lambda: self.focus_get().event_generate("<<Paste>>"))

        self.menu_run = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_run, label='Run', underline=0)
        self.menu_run.add_command(label='Generate Diff...', accelerator='F8', command=self.generate_diff)

        # context menu
        self.menu_context = self.menu_edit
        if self.tk.call('tk', 'windowingsystem') == 'aqua':
            self.bind('<2>', lambda e: self.menu_context.post(e.x_root, e.y_root))
            self.bind('<Control-1>', lambda e: self.menu_context.post(e.x_root, e.y_root))
        else:
            self.bind('<3>', lambda e: self.menu_context.post(e.x_root, e.y_root))

        # Key binds
        self.bind("<F8>", self.generate_diff)

    def generate_diff(self, *args, **kwargs):
        # Define TopLevel window
        diff_result_window = tk.Toplevel(self)
        diff_result_window.title('mdiff - Diff Result')
        diff_result_window_w = int(self.winfo_width() * 0.95)
        diff_result_window_h = height = int(self.winfo_height() * 0.95)
        diff_result_window.geometry(f'{diff_result_window_w}x{diff_result_window_h}+20+20')

        # Define DiffResult frame
        diff_result_content = DiffResult(diff_result_window)
        diff_result_content.set_diff_params(a=self.text_source.get("1.0", tk.END),
                                            b=self.text_target.get("1.0", tk.END))

        # build and show window
        diff_result_content.generate_diff()
        window = DiffResultWindowBuilder(diff_result_window, diff_result_content)
        # diff_result_window.transient(self)
        diff_result_window.focus_force()
        diff_result_window.wait_visibility()
        diff_result_window.grab_set()
        diff_result_window.wait_window()
