# -*- coding: utf-8 -*-
""" A utility to generate plots.
Todo:
    * predefine a colormap of 10 unique colors for increased visibility

"""

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from series_entry import SeriesEntry


class Plotter(tk.Toplevel):
    locslst = [
        "best",
        "upper right",
        "upper left",
        "lower left",
        "lower right",
        "right",
        "center left",
        "center right",
        "lower center",
        "upper center",
        "center"
        ]
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
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.plotstyle = tk.StringVar()
        self.loc = tk.StringVar()
        self.resizable(0, 0)
        self.build()

    def build(self):
        self.plotstyle.set('seaborn-colorblind')
        self.pmenu = tk.Menu(self)
        self.pltmenu = tk.Menu(master=self, tearoff=1)

        for style in Plotter.styles:
            self.pltmenu.add_command(
                label=style,
                command=lambda style=style: self.plotstyle.set(style)
                )

        self.pmenu.add_cascade(label="Set plot style", menu=self.pltmenu)
        # self.pmenu.add_command(label="Set figure dimensions", command=None)

        self.winfo_toplevel().config(menu=self.pmenu)
        self.winfo_toplevel().title("Plotting Utility")

        # NOTE: this is a dirty way of doing it... but it works
        tk.Label(
            master=self,
            text=(
                "File path:                           " +
                "Series title:                        " +
                "  Pressure to plot:"
                )
            ).pack(anchor=tk.W)

        self.entfrm = tk.Frame(self)  # to hold all the SeriesEntries
        for _ in range(10):
            SeriesEntry(self.entfrm).pack()
        self.entfrm.pack(side=tk.TOP)

        # to hold the settings entries
        self.setfrm = tk.Frame(self)
        self.anchorent = ttk.Entry(self.setfrm)
        self.locs = ttk.OptionMenu(
            self.setfrm,
            self.loc,
            Plotter.locslst[1],
            *Plotter.locslst)
        tk.Label(
            master=self.setfrm,
            text="Legend location:"
            ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(
            master=self.setfrm,
            text="bbox_to_anchor:"
            ).grid(row=0, column=1, sticky=tk.W)

        self.locs.grid(row=1, column=0, sticky=tk.W, padx=2)
        self.anchorent.grid(row=1, column=1, sticky=tk.E, padx=2)
        # self.anchorent.insert(0, "1.13,0.525")

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Plot",
            width=30,
            command=self.make_plot
            )
        self.pltbtn.grid(row=2, columnspan=2, pady=1)
        self.setfrm.pack(side=tk.BOTTOM)

    def make_plot(self):
        to_plot = []
        for child in self.entfrm.winfo_children():
            if not child.path.get() == "":
                to_plot.append(
                    child.path.get(),
                    child.title.get(),
                    child.plotpump.get()
                    )

        self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
        self.ax.set_xlabel("Time (min)")
        self.ax.set_xlim(left=0, right=90)
        self.ax.set_ylabel("Pressure (psi)")
        self.ax.set_ylim(top=1500)
        self.ax.yaxis.set_major_locator(MultipleLocator(100))
        self.ax.grid(color='grey', alpha=0.3)
        self.ax.set_facecolor('w')
        self.fig.canvas.set_window_title("")
        # TODO: this plt stuff can probably go elsewhere
        plt.style.use(self.plotstyle.get())
        plt.tight_layout()

        for item in to_plot:
            data = pd.read_csv(item[0])
            self.ax.plot(data['Minutes'], data[item[2]], label=item[1])

        if self.anchorent.get() == "":
            bbox = None
        else:
            bbox = tuple(map(float, self.anchorent.get().split(',')))

        self.ax.legend(loc=self.loc.get(), bbox_to_anchor=bbox)
        self.fig.show()
