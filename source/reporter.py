"""Evaluates data and makes a plot"""

from datetime import date
import matplotlib as mpl
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.ticker import MultipleLocator
import os  # handling file paths
import openpyxl
from pandas import Series, DataFrame, read_csv # reading the data
import pickle  # storing plotter settings
import PIL
import shutil
import time
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
        self.core = parent
        self.mainwin = self.core.mainwin
        self.config = self.core.config
        self.plotterstyle = tk.StringVar()
        self.loc = tk.StringVar()
        self.resizable(0, 0)
        self.build()

    def build(self)  -> None:
        """Makes the widgets"""

        self.winfo_toplevel().title("Report Generator")

        self.pltbar = tk.Menu(self)
        self.pltbar.add_command(
            label="Save project",
            command=lambda: self.pickle_plot()
        )
        self.pltbar.add_command(
            label="Load from project",
            command=lambda: self.unpickle_plot()
        )
        self.pltbar.add_command(
            label='Export report',
            command=lambda: self.export_report()
        )
        self.pltbar.add_command(
            label='Help',
            command=lambda: self.show_help()
        )

        self.winfo_toplevel().configure(menu=self.pltbar)

        # a LabelFrame to hold the SeriesEntry widgets
        self.entfrm = tk.LabelFrame(
            master=self,
            # NOTE: this is a dirty way of doing it... but it works
            text=(
                "File path:                           " +
                "Series title:                        " +
                "           Pressure to evaluate:"
                )
        )
        defpsi = self.config.get('test settings', 'default pump')
        for _ in range(self.config.getint('report settings', 'series per project')):
            SeriesEntry(self.entfrm, defpsi).grid(padx=2)
        self.entfrm.grid(row=0, padx=2)

        # to hold the settings entries
        self.setfrm = tk.LabelFrame(master=self, text="Plot parameters")

        self.stylemenu = ttk.OptionMenu(
            self.setfrm,
            self.plotterstyle,
            self.config.get('plot settings', 'default style'),
            *self.config.get('plot settings', 'plot styles').split(',')
        )
        if self.config.getboolean('plot settings', 'show style options'):
            tk.Label(
                master=self.setfrm,
                text="Plot style:"
                ).grid(row=0, column=0, sticky=tk.E, padx=5, pady=2)
            self.stylemenu.grid(row=0, column=1, sticky='w', padx=(5, 10), pady=2)

        tk.Label(
            master=self.setfrm,
            text="Time limit (min):"
            ).grid(row=0, column=2, sticky=tk.E, padx=5, pady=(10,2))
        self.xlim = ttk.Entry(self.setfrm, width=14)
        self.xlim.insert(0, self.config.get('test settings', 'time limit minutes'))
        self.xlim.grid(row=0, column=3, sticky='w', padx=5, pady=(2))

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
        self.ylim.insert(0,
            self.config.get('test settings', 'fail psi')
        )
        self.ylim.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(
            master=self.setfrm,
            text="Baseline pressure (psi):"
            ).grid(row=2, column=2, sticky=tk.E, padx=5, pady=2)
        self.baseline = ttk.Entry(self.setfrm, width=14)
        self.baseline.insert(0,
            self.config.get('test settings', 'default baseline')
        )
        self.baseline.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Evaluate",
            width=30,
            command=lambda: self.make_plot(**self.prep_plot())
        )
        self.pltbtn.grid(row=3, columnspan=4, pady=2)

        self.setfrm.grid(row=1, pady=2)

    def prep_plot(self) -> dict:
        """Returns a dict of tuples
            paths - str paths of original datafiles
            titles - str tuple of original series titles
            plotpumps - str tuple which pump's pressure to evaluate
            plot_params - a tuple of (str, int, int, (floats,))
                        last arg optional
        """

        print("Preparing plot from Reporter fields")

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
        if self.xlim.get() != '':
            xlim = int(self.xlim.get())
        else:
            xlim = self.config.getint('test settings', 'time limit minutes')

        if self.ylim.get() != '':
            ylim = int(self.ylim.get())
        else:
            ylim = self.config.getint('test settings', 'fail psi')

        if self.baseline.get() != '':
            baseline = int(self.baseline.get())
        else:
            baseline = self.config.getint('test settings', 'default baseline')

        plot_params = (self.plotterstyle.get(), xlim, ylim, baseline)

        _plt = {
                'paths' : paths,
                'titles' : titles,
                'plotpumps' : plotpumps,
                'plot_params' : plot_params
                }
        return _plt

    def make_plot(self, paths, titles, plotpumps, plot_params) -> None:
        """Makes a new plot from some tuples"""

        print("Spawning a new plot \n")
        start = time.time()
        # reset the stylesheet
        plt.rcParams.update(plt.rcParamsDefault)

        # give names to plot parameters
        style = plot_params[0]
        if plot_params[1] != '':
            xlim = plot_params[1]
        else:
            xlim = int(self.mainwin.timelim.get())

        if plot_params[2] != '':
            ylim = plot_params[2]
        else:
            ylim = int(self.mainwin.failpsi.get())

        with plt.style.context(style):
            colors = self.config.get('plot settings', 'color cycle').split(',')
            colors = [i.strip() for i in colors]
            mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color = colors)
            self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
            self.ax.set_xlabel("Time (min)")
            self.ax.set_xlim(left=0, right=xlim)
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=ylim)
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.grid(color='darkgrey', alpha=0.65, linestyle='-')
            self.ax.set_facecolor('w')
            self.fig.canvas.set_window_title(self.mainwin.title)
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
                if title == "": pass
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
            if len(blanks) == 0 and len(trials) == 0:
                tk.messagebox.showwarning(
                parent=self,
                title="No data selected",
                message="Click a 'File path:' entry to select a data file")
            elif len(blanks) == 0:
                tk.messagebox.showwarning(
                parent=self,
                title="No series designated as blank",
                message="At least one series title must contain 'blank'")
            elif len(trials) == 0:
                tk.messagebox.showwarning(
                parent=self,
                title="No trial data selected",
                message="At least one trial not titled 'blank' must be selected")
            else:
                self.evaluate(blanks, trials, baseline, xlim, ylim)
                self.fig.show()

                project = self.mainwin.project.split('\\')
                short_proj = project[-1]
                image = f"{short_proj}.png"
                image_path = os.path.join(self.mainwin.project, image)
                self.fig.savefig(image_path)
                print(f"Saved plot image to\n{image_path}")
                print(f"Finished plotting in {round(time.time() - start, 2)} s")

    def pickle_plot(self) -> None:
        """Pickles a list to a file in the project directory"""

        project = self.mainwin.project.split('\\')
        short_proj = project[-1]
        _pickle = f"{short_proj}.pct"
        _path = os.path.join(self.mainwin.project, _pickle)
        with open(_path, 'wb') as p:
            print(f"Pickling project to\n{_path}")
            pickle.dump(self.prep_plot(), file=p)
        tk.messagebox.showinfo(
            parent=self,
            title="Saved successfully",
            message=f"Project data saved to\n{_path}"
            )

    def unpickle_plot(self) -> None:
        """Unpickles/unpacks a list of string 3-tuples and puts those values
        into SeriesEntry widgets"""

        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data to plot:",
            filetypes=[("ScaleWiz project files", "*.pct")]
            )

        # this puts data paths into their original entries
        if fil != '':
            print(f"Unpickling project file\n{fil}")
            with open(fil, 'rb') as p:
                _plt = pickle.load(p)

            into_widgets = zip(
                _plt['paths'],
                _plt['titles'],
                _plt['plotpumps'],
                self.entfrm.winfo_children()
            )

            print("Populating Reporter fields")
            for path, title, plotpump, widget in into_widgets:
                widget.path.delete(0, 'end')
                widget.path.insert(0, path)
                self.after(150, widget.path.xview_moveto, 1)
                widget.title.delete(0, 'end')
                widget.title.insert(0, title)
                self.after(150, widget.title.xview_moveto, 1)
                widget.plotpump.set(plotpump)
                #  NOTE: on use of after
                #  https://stackoverflow.com/questions/29334544/

        # raise the settings window
        self.lift()

    def evaluate(self, blanks, trials, baseline, xlim, ylim):
        """Evaluates the data"""

        start=time.time()
        print("Evaluating data")
        interval = self.config.getint('test settings', 'interval seconds')
        print(f"baseline: {baseline} psi")
        print(f"xlim: {xlim*60} s")
        print(f"ylim: {ylim} psi")
        print()
        total_area = ylim*xlim*60/interval
        baseline_area = baseline*xlim*60/interval
        avail_area = total_area - baseline_area
        print(f"total_area: {total_area} psi")
        print(f"baseline_area: {baseline_area} psi")
        print(f"avail_area: {avail_area} psi")
        print(f"max measures: {xlim*60/interval}")
        print()

        blank_scores = []
        blank_times = []

        for blank in blanks:
            blank_times.append(round(len(blank)*interval, 2))
            print(blank.name)
            scale_area = blank.sum()
            print(f"scale area: {scale_area} psi")
            area_over_blank = ylim*len(blank) - scale_area
            print(f"area over blank: {area_over_blank} psi")
            protectable_area = avail_area - area_over_blank
            print(f"protectable_area: {protectable_area} psi")
            blank_scores.append(protectable_area)
            print()
        protectable_area = int(DataFrame(blank_scores).mean())
        print(f"avg protectable_area: {protectable_area} psi")
        print()

        scores = {}
        for trial in trials:
            print(trial.name)
            measures = len(trial)
            print(f"number of measurements: {measures}")
            print(f"total trial area: {trial.sum()} psi")
            # all the area under the curve + ylim per would-be measure
            scale_area = int(trial.sum() + ylim*(xlim*60/interval - measures))
            print(f"scale area {scale_area} psi")
            score = (1 - (scale_area - baseline_area)/protectable_area)*100
            print(f"score: {score:.2f}%")
            if score > 100:
                print("Reducing score to 100%")
                score = 100
            scores[trial.name] = score
            print()

        result_titles = [f"{i}" for i in scores]
        result_values = [f"{scores[i]:.1f}%" for i in scores]
        durations = [round(len(trial)*interval, 2) for trial in trials]
        max_psis = [
                    int(trial.max())
                    if int(trial.max()) <= ylim
                    else ylim
                    for trial in trials
                   ]

        self.results_queue = (
                blank_times,
                result_titles,
                result_values,
                durations,
                baseline,
                ylim,
                max_psis
        )

        result_window = tk.Toplevel(self)
        result_window.attributes('-topmost', 'true')
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

        print(f"Finished evaluation in {round(time.time() - start, 2)} s")
        print()

    def export_report(self):
        """Exports the reporter's results_queue to an .xlsx file designated
        as the template in the config file

        """

        print("Preparing export")
        start = time.time()

        template_path = os.path.normpath(
            self.config.get('report settings', 'template path')
        )
        if not os.path.isfile(template_path):
            tk.messagebox.showerror(
                parent=self,
                message=('No valid template file found.' +
                '\nYou can set the template path in Settings > Report Settings.'
                )
            )
            return

        if not hasattr(self, 'results_queue'):
            tk.messagebox.showinfo(
            parent=self,
            message="You must evaulate a set of data before exporting a report."
            )
            return

        project = self.mainwin.project.split('\\')
        sample_point = project[-1].split('-')[0]
        customer = project[-2]
        short_proj = project[-1]

        _img = f"{short_proj}.png"
        _path = os.path.join(self.mainwin.project, _img)
        print("Making temp resized plot image")
        img = PIL.Image.open(_path)
        # img = img.resize((700, 265))
        img = img.resize((667, 257))
        _path = _path[:-4]
        _path += "- temp.png"
        img.save(_path)
        img = openpyxl.drawing.image.Image(_path)
        img.anchor = 'A28'

        file = f"#-# {short_proj} Calcium Carbonate Scale Block Analysis.xlsx"
        report_path = os.path.join(self.mainwin.project, file)
        while os.path.isfile(report_path):
            report_path = report_path[:-5]
            report_path += ' - copy.xlsx'

        print(f"Copying report template to\n{report_path}")
        shutil.copyfile(template_path, report_path)

        print(f"Populating file\n{report_path}")
        wb = openpyxl.load_workbook(report_path)
        ws = wb.active
        ws._images[1] = img

        blank_times = self.results_queue[0]
        result_titles = self.results_queue[1]
        result_values = self.results_queue[2]
        durations = self.results_queue[3]
        baseline = self.results_queue[4]
        ylim = self.results_queue[5]
        max_psis = self.results_queue[6]

        # # TODO:  move this mapping into the config somehow
        ws['C4'] = customer
        ws['C7'] = sample_point
        ws['I7'] = f"{date.today()}"
        ws['D11'] = f"{baseline} psi"
        ws['G16'] = f"{ylim}"

        blank_time_cells = [f"E{i}" for i in range(16, 18)]
        chem_name_cells = [f"A{i}" for i in range(19, 27)]
        chem_conc_cells = [f"D{i}" for i in range(19, 27)]
        duration_cells = [f"E{i}" for i in range(19, 27)]
        max_psi_cells = [f"G{i}" for i in range (19, 27)]
        protection_cells = [f"H{i}" for i in range(19, 27)]

        chem_names = [title.split(' ')[0] for title in result_titles]
        chem_concs = [" ".join(title.split(' ')[1:2]) for title in result_titles]

        for (cell, blank_time) in zip(blank_time_cells, blank_times):
            ws[cell] = float(round(blank_time/60, 2))
        for (cell, name) in zip(chem_name_cells, chem_names):
            ws[cell] = name
        for (cell, conc) in zip(chem_conc_cells, chem_concs):
            ws[cell] = int(conc)
        for (cell, duration) in zip(duration_cells, durations):
            ws[cell] = float(round(duration/60, 2))
        for (cell, psi) in zip(max_psi_cells, max_psis):
            ws[cell] = int(psi)
        for (cell, score) in zip(protection_cells, result_values):
            ws[cell] = float(score)

        # note: may need to move contents up before deleting del_rows

        del_rows = []
        for i in range(19, 27):
            if ws[f'A{i}'].value == None:
                del_rows.append(i)
        if len(del_rows) == 0: pass
        for row in del_rows:
            ws.row_dimensions[row].hidden = True

        print(f"Saving file")
        wb.save(filename=report_path)
        print("Removing temp files")
        os.remove(_path)
        print(f"Finished export in {round(time.time() - start, 2)} s")
        tk.messagebox.showinfo(
            parent=self,
            message=f"Report exported to\n{report_path}"
            )

    def show_help(self):
        """Shows a help dialog to the user"""
        tk.messagebox.showinfo(
        parent=self,
        title="Help: Using the Report Generator",
        message="""
Clicking on a 'File path' field will prompt you to select the .csv file of the data you want to plot. You may change the default 'Series title' to appear on the plot.

Including the word 'blank' in a series title will designate it as such for the purposes of calculations, and will set the data to plot as a dashed line. You must select at least one blank and one non-blank set of data to evaluate results.

Save project: Saves the current Report Generator form to a .pct file

Load project: Repopulates the Report Generator form from a .pct file

Export report: Makes a copy of the file at 'Template Path' (see Report Settings) and populates it with the results of the evaluation.
"""
        )
