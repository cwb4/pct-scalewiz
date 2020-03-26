""" A custom widget for the plotter utility.

Stores three pieces of information needed to plot a series from a csv file.
Allows for easy selection of file path by calling askfil when the user
clicks the path entry widget.

Attributes:
    * file path as a string, get with .path.get()
    * series label as a string (for the legend), get with .title.get()
    * which pump's pressure to plot as a string, get with .plotpump.get()
"""

import tkinter as tk
from tkinter import ttk, filedialog

class SeriesEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.plotpump = tk.StringVar()
        self.plotpump.set("PSI 2")
        self.path = ttk.Entry(self, width=20)
        self.path.bind("<Button-1>", self.askfil)
        self.title = ttk.Entry(self, width=20)
        self.path.grid(row=0, column=0, padx=2, pady=1)
        self.title.grid(row=0, column=1, padx=2, pady=1)
        tk.Radiobutton(self, text="PSI 1", variable=self.plotpump,
            value='PSI 1').grid(row=0, column=2, padx=2, pady=1)
        tk.Radiobutton(self, text="PSI 2", variable=self.plotpump,
            value='PSI 2').grid(row=0, column=3, padx=2, pady=1)
        ttk.Button(self, text="Remove",
            command=self.clear_ents).grid(row=0, column=4, padx=2, pady=2)

    def askfil(self, event):
        fil = filedialog.askopenfilename(initialdir = "C:\"",
            title="Select data output directory:",
            filetypes=[("CSV files", "*.csv")])
        if not fil == "":
            event.widget.delete(0,tk.END)
            event.widget.insert(0,fil)
            event.widget.after(50, event.widget.xview_moveto, 1)
            event.widget.after(50, lambda: self.title.focus_set())
        # NOTE: :  for some reason this only fires if postponed
        # https://stackoverflow.com/questions/29334544/

    def clear_ents(self):
        self.path.delete(0, tk.END)
        self.title.delete(0, tk.END)
