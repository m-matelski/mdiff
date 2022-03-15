import unittest

import tkinter as tk


class Test1(unittest.TestCase):

    def test1(self):
        root = tk.Tk()
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=10)
        root.rowconfigure(1, weight=10)

        text = tk.Text(root)
        text.grid(column=0, row=1)

        top_frame = tk.Frame(root)
        top_frame.grid(column=0, row=0)

        labels = 10
        for i in range(labels):
            label = tk.Label(top_frame, text=f'label_{i}')
            # label.pack(side='left', expand=False)
            label.grid(column=i, row=0)
        # lbl1 = tk.Label(top_frame, text="label1")
        # lbl2 = tk.Label(top_frame, text="label2")
        # lbl3 = tk.Label(top_frame, text="label3")
        #
        # lbl1.pack(side="left")
        # lbl2.pack(side="left")
        # lbl3.pack(side="left")

        root.mainloop()
