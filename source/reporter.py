"""Evaluates data and makes a plot"""

import matplotlib as mpl
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.ticker import MultipleLocator
import os  # handling file paths
from pandas import Series, DataFrame, read_csv # reading the data
import pickle  # storing plotter settings
import tkinter as tk  # GUI
from tkinter import ttk, filedialog, messagebox

from seriesentry import SeriesEntry


class Reporter(tk.Toplevel):
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

    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.mainwin = parent.parent
        self.core = parent.parent.parent
        self.plotterstyle = tk.StringVar()
        self.loc = tk.StringVar()
        self.resizable(0, 0)
        self.build()

    def build(self)  -> None:
        """Makes the widgets"""
        self.winfo_toplevel().title("Report Generator")

        self.pltbar = tk.Menu(self)
        self.pltbar.add_command(
            label="Save project settings",
            command=lambda: self.pickle_plot()
            )
        self.pltbar.add_command(
            label="Load from project settings",
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
                "           Pressure to evaluate:"
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
            self.core.PLOT_STYLES[0],
            *self.core.PLOT_STYLES
            )
        self.stylemenu.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        tk.Label(
            master=self.setfrm,
            text="Time limit (min):"
            ).grid(row=0, column=2, sticky=tk.E, padx=5, pady=(10,2))
        self.xlim = ttk.Entry(self.setfrm, width=14)
        self.xlim.insert(0, self.mainwin.timelim.get())
        self.xlim.grid(row=0, column=3, sticky=tk.W, padx=5, pady=(2))

        tk.Label(
            master=self.setfrm,
            text="Legend location:"
            ).grid(row=1, column=0, sticky=tk.E, padx=5, pady=2)
        self.locsmenu = ttk.OptionMenu(
            self.setfrm,
            self.loc,
            Reporter.LocsLst[1],
            *Reporter.LocsLst
            )
        self.locsmenu.grid(row=1, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        tk.Label(
            master=self.setfrm,
            text="Max pressure (psi):"
            ).grid(row=1, column=2, sticky=tk.E, padx=5, pady=2)
        self.ylim = ttk.Entry(self.setfrm, width=14)
        self.ylim.insert(0, self.mainwin.failpsi.get())
        self.ylim.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="Baseline pressure (psi):"
            ).grid(row=2, column=2, sticky=tk.E, padx=5, pady=2)
        self.baseline = ttk.Entry(self.setfrm, width=14)
        self.baseline.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Evaluate",
            width=30,
            command=lambda: self.make_plot(**self.prep_plot())
            )
        self.pltbtn.grid(row=3, columnspan=4, pady=2)

        self.setfrm.grid(row=1, pady=2)

    def prep_plot(self) -> "dict":
        """Returns a dict of
            paths - paths of original datafiles
            this_data - a tuple of pandas dataframes of the original data
            series_titles - str tuple of original series titles
            plotpumps - tuple of bools whether to plot 'PSI 1'
            plot_params - a tuple of (str, int, int, (floats,))
                        last arg optional
        """

        paths = tuple(
            [
            child.path.get()
            for child in self.entfrm.winfo_children()
            ]
        )

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

        # look for empty entries in the form
        if self.xlim.get() is not '':
            xlim = int(self.xlim.get())
        else:
            xlim = int(self.mainwin.timelim.get())

        if self.ylim.get() is not '':
            ylim = int(self.ylim.get())
        else:
            ylim = int(self.mainwin.failpsi.get())

        if self.baseline.get() is not '':
            baseline = int(self.baseline.get())
        else:
            baseline = 0

        plot_params = (self.plotterstyle.get(), xlim, ylim, baseline)

        _paths = [i for i in paths]
        _titles = [i for i in titles]
        _plotpumps = [i for i in plotpumps]
        _plot_params = plot_params

        _plt = {
                'paths' : _paths,
                'titles' : _titles,
                'plotpumps' : _plotpumps,
                'plot_params' : _plot_params
                }
        return _plt

    def make_plot(self, paths, titles, plotpumps, plot_params) -> None:
        """Makes a new plot from some tuples"""

        # unpack values from _plt here

        # reset the stylesheet
        plt.rcParams.update(plt.rcParamsDefault)

        # give names to plot parameters
        style = plot_params[0]
        if plot_params[1] is not '':
            xlim = int(plot_params[1])
        else:
            xlim = int(self.mainwin.timelim.get())

        if plot_params[2] is not '':
            ylim = int(plot_params[2])
        else:
            ylim = int(self.mainwin.failpsi.get())

        with plt.style.context(style):
            mpl.rcParams['axes.prop_cycle'] = mpl.cycler(
                color = self.core.COLOR_CYCLE
                )
            self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
            self.ax.set_xlabel("Time (min)")
            self.ax.set_xlim(left=0, right=xlim)
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=ylim)
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.grid(color='darkgrey', alpha=0.65, linestyle='-')
            self.ax.set_facecolor('w')
            self.fig.canvas.set_window_title("")
            plt.tight_layout()

            blanks = []
            trials = []
            # NOTE: to_plot = [(0: path, 1: title, 2: plotpump)]
            for path, title, plotpump in zip(paths, titles, plotpumps):
                # print(path, title, plotpump)
                if os.path.isfile(path):
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
                    blanks.append(Series(df[plotpump], name=title))

                else:  # plot using default line style
                    self.ax.plot(df['Minutes'], df[plotpump],
                        label=title
                        )
                    trials.append(Series(df[plotpump], name=title))

            self.ax.legend(loc=self.loc.get())

            baseline = plot_params[3]

            # some tests to validate user input
            if len(blanks) is 0 and len(trials) is 0:
                tk.messagebox.showwarning(
                master=self,
                title="No data selected",
                message="Click a 'File path:' entry to select a data file")
                self.lift()
            elif len(blanks) is 0:
                tk.messagebox.showwarning(
                master=self,
                title="No series designated as blank",
                message="At least one series title must contain 'blank'")
                self.lift()
            elif len(trials) is 0:
                tk.messagebox.showwarning(
                master=self,
                title="No trial data selected",
                message="At least one trial not titled 'blank' must be selected")
                self.lift()
            else:
                if baseline is 0:
                    baseline = 75
                    tk.messagebox.showwarning(
                    title="No baseline pressure designated",
                    message=f"A default value of {baseline} psi will be used")
                    self.lift()
                self.evaluate(blanks, trials, baseline, xlim, ylim)
                self.fig.show()

    def pickle_plot(self) -> None:
        """Pickles a list to a file in the project directory"""

        project = self.mainwin.project.split('\\')
        short_proj = project[-1]
        _pickle = f"{short_proj}.pct"
        _path = os.path.join(self.mainwin.project, _pickle)
        with open(_path, 'wb') as p:
            pickle.dump(self.prep_plot(), file=p)
        tk.messagebox.showinfo(
            message=f"Project data saved to \n {_path}"
            )
        self.lift()

    def unpickle_plot(self) -> None:
        """Unpickles/unpacks a list of string 3-tuples and puts those values
        into SeriesEntry widgets"""

        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data to plot:",
            filetypes=[("Plot settings", "*.pct")]
            )

        # this puts data paths into their original entries
        if fil is not '':
            with open(fil, 'rb') as p:
                _plt = pickle.load(p)

            into_widgets = zip(
                _plt['paths'],
                _plt['titles'],
                _plt['plotpumps'],
                self.entfrm.winfo_children()
            )

            for path, title, plotpump, widget in into_widgets:
                widget.path.delete(0, tk.END)
                widget.path.insert(0, path)
                self.after(150, widget.path.xview_moveto, 1)
                widget.title.delete(0, tk.END)
                widget.title.insert(0, title)
                self.after(150, widget.title.xview_moveto, 1)
                widget.plotpump.set(plotpump)
                #  NOTE: on use of after
                #  https://stackoverflow.com/questions/29334544/

        # raise the settings window
        self.lift()

    def evaluate(self, blanks, trials, baseline, xlim, ylim):
        print(f"baseline: {baseline}")
        print(f"xlim: {xlim}")
        print(f"ylim: {ylim}")
        print()
        total_area = ylim*xlim*60
        baseline_area = baseline*xlim*60
        avail_area = total_area - baseline_area
        print(f"total_area: {total_area}")
        print(f"baseline_area: {baseline_area}")
        print(f"avail_area: {avail_area}")
        print()

        blank_scores = []
        for blank in blanks:
            print(blank.name)
            scale_area = blank.sum()
            print(f"scale area: {scale_area}")
            area_over_blank = ylim*len(blank) - scale_area
            print(f"area over blank: {area_over_blank}")
            protectable_area = avail_area - area_over_blank
            print(f"protectable_area: {protectable_area}")
            blank_scores.append(protectable_area)
            print()
        protectable_area = int(DataFrame(blank_scores).mean())
        print(f"avg protectable_area: {protectable_area}")
        print()

        scores = {}
        for trial in trials:
            print(trial.name)
            measures = len(trial)
            # disregard data taken past the timelimit
            if measures > xlim*60: measures = xlim*60
            print(f"number of measurements: {measures}")
            scale_area = int(trial.sum() + ylim*(xlim*60 - measures))
            print(f"scale area {scale_area}")
            score = 1 - (scale_area - baseline_area)/protectable_area
            print(f"ratio used: {score:.2f}")
            if score*100 > 100: score = 100
            else: score = score*100
            scores[trial.name] = score
            print()

        result_titles = [f"{i}" for i in scores]
        result_values = [f"{scores[i]:.1f}%" for i in scores]

        result_window = tk.Toplevel(self)
        result_window.title("Results")
        def_bg = result_window.cget('bg')
        for i, title in enumerate(result_titles):
            e = tk.Label(result_window, text=title)
            e.grid(row=i, column=0, padx=(45))

        for i, value in enumerate(result_values):
            e = tk.Entry(result_window, bg=def_bg, width=10)
            e.insert(0, value)
            e.configure(state='readonly', relief='flat')
            e.grid(row=i, column=1, sticky='W')
