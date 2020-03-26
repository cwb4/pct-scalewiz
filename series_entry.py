""" A custom widget for the plotter utility.

Stores three pieces of information needed to plot a series from a csv file.
Allows for easy selection of file path by calling askfil when the user
clicks the path entry widget.

Attributes:
    * file path as a string, accessed by calling .get_path on the instance
    * series label as a string (for the legend), accessed by calling .get_title
    * which pump's pressure to plot as a string, accessed by calling .get_pump
"""

import tkinter as tk
from tkinter import ttk, filedialog

class SeriesEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.plotpump = tk.StringVar()
        self.plotpump.set("PSI 2")
        self.pathent = ttk.Entry(self, width=20)
        self.pathent.bind("<Button-1>", self.askfil)
        self.titleent = ttk.Entry(self, width=20)
        self.pathent.grid(row=0, column=0, padx=2, pady=1)
        self.titleent.grid(row=0, column=1, padx=2, pady=1)
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
        event.widget.delete(0,tk.END)
        event.widget.insert(0,fil)
        event.widget.after(50, event.widget.xview_moveto, 1)
        # NOTE: :  for some reason this only fires if postponed
        # https://stackoverflow.com/questions/29334544/

    def clear_ents(self):
        self.pathent.delete(0, tk.END)
        self.titleent.delete(0, tk.END)
