# -*- coding: utf-8 -*-
""" The main window's menubar.


"""

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

class SerEnt(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.plotpump = tk.StringVar()
        self.plotpump.set("PSI 2")
        self.pathent = ttk.Entry(self, width=20)
        self.pathent.bind("<Button-1>", self.askfil)
        self.titleent = ttk.Entry(self, width=20)
        self.pathent.grid(row=0, column=0, padx=2, pady=1)
        self.titleent.grid(row=0, column=1, padx=2, pady=1)
        tk.Radiobutton(self, text="PSI 1", variable=self.plotpump, value='PSI 1').grid(row=0, column=2, padx=2, pady=1)
        tk.Radiobutton(self, text="PSI 2", variable=self.plotpump, value='PSI 2').grid(row=0, column=3, padx=2, pady=1)
        ttk.Button(self, text="Remove", command=self.clear_ents).grid(row=0, column=4, padx=2, pady=2)

        # NOTE: these could be useful (?)
        self.get_path = self.pathent.get()
        self.get_title = self.titleent.get()
        self.get_pump = self.plotpump.get()

    def askfil(self, event):
        fil = filedialog.askopenfilename(initialdir = "C:\"",title="Select data output directory:", filetypes=[("CSV files", "*.csv")])
        event.widget.delete(0,tk.END)
        event.widget.insert(0,fil)
        event.widget.after(50, event.widget.xview_moveto, 1)  # BUG:  for some reason this only fires if postponed
        # https://stackoverflow.com/questions/29334544/why-does-tkinters-entry-xview-moveto-fail

    def clear_ents(self):
        self.pathent.delete(0, tk.END)
        self.titleent.delete(0, tk.END)

class PlotUtil(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.winfo_toplevel().title("Plotting Utility")
        self.resizable(0,0)
        self.build()

    def build(self):
        tk.Label(self, text="File path:                           Series title:").pack(side=tk.TOP, anchor=tk.W)
        self.entfrm = tk.Frame(self)
        fields = ["ser0", "ser1", "ser2", "ser3", "ser4", "ser5", "ser6", "ser7", "ser8", "ser9"]
        for i, ent in enumerate(fields):
            self.ent = SerEnt(self.entfrm).pack()
        self.entfrm.pack(side=tk.TOP)

        self.setfrm = tk.Frame(self)
        self.anchorent = ttk.Entry(self.setfrm)
        self.locent = ttk.Entry(self.setfrm)
        tk.Label(self.setfrm, text="loc:").grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.setfrm, text="bbox_to_anchor:").grid(row=0, column=1, sticky=tk.W)
        self.locent.grid(row=1, column=0, sticky=tk.W, padx=2) # TODO: this spacing??
        self.anchorent.grid(row=1, column=1, sticky=tk.E, padx=2)
        self.pltbtn = ttk.Button(self.setfrm, text="Plot", width=30, command = self.make_plot)
        self.pltbtn.grid(row=2, columnspan=2, pady=1)
        self.setfrm.pack(side=tk.BOTTOM)

    def make_plot(self):
        # path, title, and the plotpump
        to_plot = []
        for child in self.entfrm.winfo_children():
            to_plot.append((child.get_path, child.get_title, child.get_pump))
        print(to_plot)
        #fig, ax = plt.subplot()
