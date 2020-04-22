"""The MenuBar for the MainWindow"""

import tkinter as tk  # GUI
from tkinter import filedialog
import os  # handling file paths

# from plotter import Plotter
from reporter import Reporter


class MenuBar(tk.Frame):
    styles = [
        "bmh",
        "fivethirtyeight",
        "seaborn",
        "seaborn-colorblind",
        "seaborn-dark-palette",
        "seaborn-muted",
        "seaborn-notebook",
        "seaborn-paper",
        "seaborn-pastel",
        "tableau-colorblind10"
        ]

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.build()

    def build(self):
        self.menubar = tk.Menu(self)
        # self.filemenu = tk.Menu(self, tearoff=0)
        self.menubar.add_command(
            label="Set project folder",
            command=self.askdir
            )
        self.pltmenu = tk.Menu(master=self, tearoff=0)
        self.pltstylmenu = tk.Menu(master=self, tearoff=1)
        for style in MenuBar.styles:
            self.pltstylmenu.add_command(
                label=style,
                command=lambda s = style: self.set_plotstyle(s)
                )

        self.pltmenu.add_command(label="Make new plot", command=self.new_plot)
        self.pltmenu.add_cascade(label="Set plot style", menu=self.pltstylmenu)
        # self.menubar.add_cascade(label="Set project folder", menu=self.filemenu)
        self.menubar.add_cascade(label="Plot", menu=self.pltmenu)
        self.parent.winfo_toplevel().config(menu=self.menubar)

    def askdir(self):
        """Creates a prompt to ask user for a project folder,
         then sets that as the window title.
         The project variable is a string used to make output file paths later
         """

        out = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select data output directory:"
            )

        if out != "":
            self.parent.project = os.path.abspath(out)

            # make it the MainWindow title in a pretty way
            p = out.split('/')
            pp = p[-2] + " - " + p[-1]
            self.parent.winfo_toplevel().title(pp)

    def set_plotstyle(self, style: str) -> None:
        """Sets the plot style for MainWindow"""
        self.parent.plotstyle = style

    def new_plot(self):
        """Spawns a new Plotter window"""
        # self.parent.plotter = Plotter(self)
        self.parent.reporter = Reporter(self)
