# -*- coding: utf-8 -*-
""" The main window's menubar.


"""
import tkinter as tk
from tkinter import ttk

class MenuBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pack()

    self.menubar = tk.Menu(parent)
    self.filemenu = tk.Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label=self.savepath.get(), command=self.askdir)
    self.pltmenu = tk.Menu(self.menubar, tearoff=0)
    self.pltmenu.add_command(label="Add blanks to live plot")
    self.pltmenu.add_command(label="Make new plot", command=self.new_plot)
    self.menubar.add_cascade(label="File", menu=self.filemenu)
    self.menubar.add_cascade(label="Plot", menu=self.pltmenu)
    root.config(menu=self.menubar)

    def askdir(self):
        out = filedialog.askdirectory(initialdir = "C:\"",title="Select data output directory:")
        if out == "":
            pass
        else:
            self.savepath.set(out)
            p = self.savepath.get().split('/')
            pp = p[-2] + " - " + p[-1]
            self.filemenu.entryconfig(index=1, label=pp)
            self.project.set(pp)
            root.title(self.project.get())
