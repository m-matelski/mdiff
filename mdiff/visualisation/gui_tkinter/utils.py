import tkinter as tk
from abc import ABC, abstractmethod
from typing import Union


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


class WindowBuilder(ABC):
    """
    Wrapper class for tkinter window. A window might be instance of Tk or TopLevel class.
    It can be defined to build single content frame into any of those two window types
    without duplicating code, as Tk and TopLevel has the same interfaces (for example: resizing, menu bars etc.)
    """
    def __init__(self, window: Union[tk.Tk, tk.Toplevel], content: tk.Frame):
        self.window = window
        self.content = content
