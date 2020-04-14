"""The window used for plotting, spawned by MenuBar"""
import matplotlib as mpl
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.ticker import MultipleLocator
import os  # handling file paths
from pandas import DataFrame, read_csv # reading the data
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
            command=lambda: self.pickle_plot()
            )
        self.pltbar.add_command(
            label="Load from plot settings",
            command=lambda: self.unpickle_plot()
            )
        self.winfo_toplevel().config(menu=self.pltbar)

        # a LabelFrame to hold the SeriesEntry widgets
        self.entfrm = tk.LabelFrame(
            master=self,
            # NOTE: this is a dirty way of doing it... but it works
            text=(
                "File path:                           " +
                "Series title:                        " +
                "           Pressure to plot:"
                )
            )  # to hold all the SeriesEntries
        for _ in range(10):
            SeriesEntry(self.entfrm).grid(padx=2)
        self.entfrm.grid(row=0, padx=2)

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
        self.stylemenu.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        tk.Label(
            master=self.setfrm,
            text="x limit:"
            ).grid(row=0, column=2, sticky=tk.E, padx=5, pady=(10,2))
        self.xlim = ttk.Entry(self.setfrm, width=14)
        self.xlim.grid(row=0, column=3, sticky=tk.W, padx=5, pady=(5,2))

        tk.Label(
            master=self.setfrm,
            text="Legend location:"
            ).grid(row=1, column=0, sticky=tk.E, padx=5, pady=2)
        self.locsmenu = ttk.OptionMenu(
            self.setfrm,
            self.loc,
            Plotter.LocsLst[1],
            *Plotter.LocsLst
            )
        self.locsmenu.grid(row=1, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        tk.Label(
            master=self.setfrm,
            text="y limit:"
            ).grid(row=1, column=2, sticky=tk.E, padx=5, pady=2)
        self.ylim = ttk.Entry(self.setfrm, width=14)
        self.ylim.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="bbox_to_anchor:"
            ).grid(row=2, column=0, sticky=tk.E, padx=5, pady=2)
        self.anchorent = ttk.Entry(self.setfrm, width=14)
        self.anchorent.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Plot",
            width=30,
            command=lambda: self.prep_make()
            )
        self.pltbtn.grid(row=3, columnspan=4, pady=2)

        self.setfrm.grid(row=1, pady=2)

    def prep_plot(self) -> "tuple of 5 tuples":
        """Returns a tuple of
            paths - paths of original datafiles
            this_data - a tuple of pandas dataframes of the original data
            series_titles - str tuple of original series titles
            plotpumps - tuple of bools whether to plot 'PSI 1'
            plot_params - a tuple of (str, int, int, (floats,))
                        last arg optional
        """

        # self.series_entries = [child for child in self.entfrm.winfo_children()]

        paths = tuple(
            [
            child.path.get()
            for child in self.entfrm.winfo_children()
            ]
        )

        # dfs = tuple(
        #     [
        #     DataFrame(read_csv(path))
        #     for path in paths
        #     ]
        # )

        titles = tuple(
            [
            child.title.get()
            for child in self.entfrm.winfo_children()
            ]
        )

        plotpumps = tuple(
            [
            child.plotpump.get()
            for child in self.entfrm.winfo_children()
            ]
        )

        if self.anchorent.get() is "":  # the default value
            bbox = None
        else:
            # cast it into a tuple of floats to pass to pyplot
            bbox = tuple(map(float, self.anchorent.get().split(',')))

        plot_params = (
                    self.plotterstyle.get(),
                    int(self.xlim.get()),
                    int(self.ylim.get()),
                    bbox  # tuple of floats or None
                     )


        # _paths = [i for i in paths]
        # _titles = [i for i in titles]
        # _plotpumps = [i for i in plotpumps]
        # _plot_params = plot_params

        return (paths, titles, plotpumps, plot_params)

    def prep_make(self):
        _plt = self.prep_plot()
        _paths = [i for i in _plt[0]]
        _titles = [i for i in _plt[1]]
        _plotpumps = [i for i in _plt[2]]
        _plot_params = _plt[3]

        self.make_plot(_paths, _titles, _plotpumps, _plot_params)

        # _plt = self.prep_plot()
        # [print(i) for i in _plt]
        # print()
        #


        # _paths = [_plt[i][0] for i in range(len(_plt))]



    def make_plot(self, paths, titles, plotpumps, plot_params) -> None:
        """Makes a new plot from some tuples"""

        # unpack values from _plt here

        # reset the stylesheet
        plt.rcParams.update(plt.rcParamsDefault)
        style = plot_params[0]
        xlim = plot_params[1]
        ylim = plot_params[2]
        bbox = plot_params[3]

        with plt.style.context(style):
            mpl.rcParams['axes.prop_cycle'] = mpl.cycler(
            color = [
                'orange', 'blue', 'red',
                'teal', 'magenta', 'green',
                 'purple', 'yellow', 'brown', 'darkgreen'
                 ]
            )
            self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
            self.ax.set_xlabel("Time (min)")
            self.ax.set_xlim(left=0, right=xlim)
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=ylim)
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.fig.canvas.set_window_title("")
            plt.tight_layout()

            # NOTE: to_plot = [(0: path, 1: title, 2: plotpump)]
            for path, title, plotpump in zip(paths, titles, plotpumps):
                # print(path, title, plotpump)
                if os.path.exists(path):
                    df = DataFrame(read_csv(path))
                else:
                    df = DataFrame(data={'Minutes': [0], 'PSI 1': [0], 'PSI 2': [0]})
                # if the trial is a blank run change the line style
                if title is "": pass
                elif "blank" in str(title).lower():
                    self.ax.plot(df['Minutes'], df[plotpump],
                        label=title,
                        linestyle=('-.')
                        )
                else:  # plot using default line style
                    self.ax.plot(df['Minutes'], df[plotpump],
                        label=title
                        )

            self.ax.legend(loc=self.loc.get(), bbox_to_anchor=bbox)
            self.fig.show()

    def pickle_plot(self) -> None:
        """Pickles a list to a file in the project directory"""

        project = self.mainwin.project
        path = os.path.join(project, "plot.plt")
        self.mainwin.to_log("Saving plot settings to")
        self.mainwin.to_log(path)

        with open(path, 'wb') as p:
            pickle.dump(_paths, _titles, _plotpumps, _plot_params, p)

    def unpickle_plot(self) -> None:
        """Unpickles/unpacks a list of string 3-tuples and puts those values
        into SeriesEntry widgets"""

        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data to plot:",
            filetypes=[("Plot settings", "*.plt")]
            )

        # this puts data paths into their original entries
        if fil is not '':
            with open(fil, 'rb') as p:
                _plt = pickle.load(p)
                _paths = [_plt[i][0] for i in range(10)]
                # _dfs = [_plt[i][1] for i in range(10)]
                _titles = [_plt[i][2] for i in range(10)]
                _plotpump = [_plt[i][3] for i in range(10)]
                _plt_params = _plt[4]

            # into_widgets = zip(_paths, _titles, self.series_entries)
            # for path, title, widget in into_widgets:
            #     widget.path.delete(0, tk.END)
            #     widget.path.insert(0, path)
            #     self.after(200, widget.title.xview_moveto, 1)
            #     widget.title.delete(0, tk.END)
            #     widget.title.insert(0, title)
            #     self.after(200, widget.title.xview_moveto, 1)
            #     if plotpump: widget.plotpump.set("PSI 1")
                # NOTE: on use of after
                # https://stackoverflow.com/questions/29334544/

        # raise the settings window
        self.lift()
