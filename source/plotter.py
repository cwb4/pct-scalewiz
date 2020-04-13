"""The window used for plotting, spawned by MenuBar"""

import matplotlib.pyplot as plt  # plotting the data
from matplotlib.ticker import MultipleLocator
import os  # handling file paths
from pandas import read_csv  # reading the data
import pickle  # storing plotter settings
import tkinter as tk  # GUI
from tkinter import ttk, filedialog

from seriesentry import SeriesEntry


class Plotter(tk.Toplevel):
    LocsLst = [  # list of legend locations - used in a widget
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
    Styles = [  # list of matplotlib styles - used in a widget
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
        self.mainwin = parent.parent
        self.plotterstyle = tk.StringVar()
        self.loc = tk.StringVar()
        self.resizable(0, 0)
        self.build()

    def build(self)  -> None:
        """Makes the widgets"""
        self.winfo_toplevel().title("Plotting Utility")

        self.pltbar = tk.Menu(self)
        self.pltbar.add_command(
            label="Save plot settings",
            command=lambda: self.pickle_plot(self.prep_plot())
            )
        self.pltbar.add_command(
            label="Load from plot settings",
            command=self.unpickle_plot
            )
        self.winfo_toplevel().config(menu=self.pltbar)

        # a LabelFrame to hold the SeriesEntry widgets
        self.entfrm = tk.LabelFrame(
            master=self,
            # NOTE: this is a dirty way of doing it... but it works
            text=(
                "File path:                           " +
                "Series title:                        " +
                "  Pressure to plot:"
                )
            )  # to hold all the SeriesEntries
        for _ in range(10):
            SeriesEntry(self.entfrm).grid(padx=2)
        self.entfrm.grid(row=0)

        # to hold the settings entries
        self.setfrm = tk.LabelFrame(master=self, text="Plot parameters")
        tk.Label(
            master=self.setfrm,
            text="Plot style:"
            ).grid(row=0, column=0, sticky=tk.E, padx=5, pady=2)
        self.stylemenu = ttk.OptionMenu(
            self.setfrm,
            self.plotterstyle,
            Plotter.Styles[3],
            *Plotter.Styles
            )
        self.stylemenu.grid(row=0, column=1, sticky=tk.W, padx=5)

        tk.Label(
            master=self.setfrm,
            text="Legend location:"
            ).grid(row=1, column=0, sticky=tk.E, padx=5, pady=2)
        self.locs = ttk.OptionMenu(
            self.setfrm,
            self.loc,
            Plotter.LocsLst[1],
            *Plotter.LocsLst
            )
        self.locs.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="bbox_to_anchor:"
            ).grid(row=2, column=0, sticky=tk.E, padx=5, pady=2)
        self.anchorent = ttk.Entry(self.setfrm, width=14)
        self.anchorent.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="x limit:"
            ).grid(row=3, column=0, sticky=tk.E, padx=5, pady=2)
        self.xlim = ttk.Entry(self.setfrm, width=14)
        self.xlim.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="y limit:"
            ).grid(row=4, column=0, sticky=tk.E, padx=5, pady=2)
        self.ylim = ttk.Entry(self.setfrm, width=14)
        self.ylim.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Plot",
            width=30,
            command=lambda: self.make_plot(self.prep_plot())
            )
        self.pltbtn.grid(row=5, columnspan=2, pady=2)

        self.setfrm.grid(row=1)

    def prep_plot(self) -> [(str, str, str),]:
        """Returns a list of 3-tuples of strings from the SeriesEntry widgets;
        the csv path, the label for the legend,
        and which column of the data to plot"""

        to_plot = []
        for child in self.entfrm.winfo_children():
            to_plot.append((
                    child.path.get(),
                    child.title.get(),
                    child.plotpump.get()
                    ))
        return(to_plot)

    def make_plot(self, to_plot) -> None:
        """Makes a new plot from a list of string 3-tuples (see prep_plot)"""

        # filter out the blank entries
        to_plot = [x for x in to_plot if not x[0] == ""]
        # reset the stylesheet
        plt.rcParams.update(plt.rcParamsDefault)
        with plt.style.context(self.plotterstyle.get()):
            self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
            self.ax.set_xlabel("Time (min)")
            self.ax.set_xlim(left=0, right=90)
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=1500)
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.fig.canvas.set_window_title("")
            plt.tight_layout()

            for item in to_plot:
                data = read_csv(item[0])
                self.ax.plot(data['Minutes'], data[item[2]], label=item[1])

            if self.anchorent.get() == "":
                bbox = None
            else:
                bbox = tuple(map(float, self.anchorent.get().split(',')))

            self.ax.legend(loc=self.loc.get(), bbox_to_anchor=bbox)
            self.fig.show()

    def pickle_plot(self, to_plot) -> None:
        """Pickles a list to a file in the project directory"""
        project = self.mainwin.project
        path = os.path.join(project, f"{project}.plt")
        self.mainwin.to_log("Saving plot settings to")
        self.mainwin.to_log(self.mainwin.project)
        with open(path, 'wb') as p:
            pickle.dump(to_plot, p)

    def unpickle_plot(self) -> None:
        """Unpickles/unpacks a list of string 3-tuples and puts those values
        into SeriesEntry widgets"""

        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data to plot:",
            filetypes=[("Plot settings", "*.plt")]
            )

        # this puts the pickled to_plot list back into its original entries
        with open(fil, 'rb') as p:
            to_plot = pickle.load(p)
        plotting = list(zip(to_plot, self.entfrm.winfo_children()))
        for item in plotting:
            item[1].path.delete(0, tk.END)
            item[1].path.insert(0, item[0][0])
            self.after(200, item[1].path.xview_moveto, 1)
            item[1].title.delete(0, tk.END)
            item[1].title.insert(0, item[0][1])
            self.after(200, item[1].title.xview_moveto, 1)
            # NOTE: on use of after
            # https://stackoverflow.com/questions/29334544/

        # raise the settings window
        # relative to the main window
        self.lift()
        self.make_plot(self.prep_plot())
