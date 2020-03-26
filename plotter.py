# -*- coding: utf-8 -*-
""" A
Todo:
    * enable plotting

"""

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from series_entry import SeriesEntry

class PlotUtil(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.winfo_toplevel().title("Plotting Utility")
        self.resizable(0,0)
        self.build()

    def build(self):
        # NOTE: this is a dirty way of doing it... but it works
        tk.Label(self, text=("File path:                           "+
            "Series title:")).pack(anchor=tk.W)
        self.entfrm = tk.Frame(self) # to hold all the SeriesEntries
        for _ in range(10):
            SeriesEntry(self.entfrm).pack()
        self.entfrm.pack(side=tk.TOP)

        # to hold the settings entries
        self.setfrm = tk.Frame(self)
        self.anchorent = ttk.Entry(self.setfrm)
        self.locent = ttk.Entry(self.setfrm)
        tk.Label(self.setfrm,
         text="loc:").grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.setfrm,
         text="bbox_to_anchor:").grid(row=0, column=1, sticky=tk.W)
        self.locent.grid(row=1, column=0, sticky=tk.W, padx=2)
        self.anchorent.grid(row=1, column=1, sticky=tk.E, padx=2)
        self.pltbtn = ttk.Button(self.setfrm,
         text="Plot", width=30, command = self.make_plot)
        self.pltbtn.grid(row=2, columnspan=2, pady=1)
        self.setfrm.pack(side=tk.BOTTOM)

    def make_plot(self):
        to_plot = []
        for child in self.entfrm.winfo_children():
            if not child.pathent.get() == "":
                to_plot.append((child.pathent.get(), child.titleent.get(),
                 child.plotpump.get()))
        self.fig, self.ax = plt.subplots(figsize=(7.5,4), dpi=100)
        self.ax.set_xlabel("Time (min)")
        self.ax.set_xlim(left=0,right=90)
        self.ax.set_ylabel("Pressure (psi)")
        self.ax.set_ylim(top=1500)
        self.ax.yaxis.set_major_locator(MultipleLocator(100))
        self.ax.grid(color='grey', alpha=0.3)
        self.ax.set_facecolor('w')

        for item in to_plot:
            print(item)
            data = pd.read_csv(item[0])
            self.ax.plot(data['Minutes'], data[item[2]], label=item[1])
        self.ax.legend(loc=0)
        self.fig.show()
