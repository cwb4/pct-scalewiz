import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
import pickle

from seriesentry import SeriesEntry


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
        self.plotterstyle = tk.StringVar()
        self.loc = tk.StringVar()
        self.resizable(0, 0)
        self.build()

    def build(self):
        self.winfo_toplevel().title("Plotting Utility")

        self.pltbar = tk.Menu(self)
        self.pltmnu = tk.Menu(self, tearoff=0)
        self.pltmnu.add_command(
            label="Save plot settings",
            command = lambda: self.pickle_plot(self.prep_plot())
            )
        self.pltmnu.add_command(
            label="Load from plot settings",
            command = self.unpickle_plot
            )
        self.pltbar.add_cascade(label="Plot", menu=self.pltmnu)
        self.winfo_toplevel().config(menu=self.pltbar)

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

        self.styles = ttk.OptionMenu(
            self.setfrm,
            self.plotterstyle,
            Plotter.styles[3],
            *Plotter.styles)

        tk.Label(
            master=self.setfrm,
            text="Plot style:"
            ).grid(row=0, column=0, sticky=None)
        tk.Label(
            master=self.setfrm,
            text="Legend location:"
            ).grid(row=0, column=1, sticky=None)
        tk.Label(
            master=self.setfrm,
            text="bbox_to_anchor:"
            ).grid(row=0, column=2, sticky=None)

        self.styles.grid(row=1, column=0, sticky=tk.W, padx=2)
        self.locs.grid(row=1, column=1, sticky=tk.W, padx=2)
        self.anchorent.grid(row=1, column=2, sticky=tk.E, padx=2)
        # self.anchorent.insert(0, "1.13,0.525")

        self.pltbtn = ttk.Button(
            master=self.setfrm,
            text="Plot",
            width=30,
            command= lambda: self.make_plot(self.prep_plot())
            )
        self.pltbtn.grid(row=2, columnspan=3, pady=1)
        self.setfrm.pack(side=tk.BOTTOM)

    def prep_plot(self):
        to_plot = []
        for child in self.entfrm.winfo_children():
            if not child.path.get() == "":
                to_plot.append((
                    child.path.get(),
                    child.title.get(),
                    child.plotpump.get()
                    ))
        return(to_plot)

    def make_plot(self, to_plot):
        plt.rcParams.update(plt.rcParamsDefault)
        with plt.style.context(self.plotterstyle.get()):
            self.fig, self.ax = plt.subplots(figsize=(12.5, 5), dpi=100)
             # refresh the style
            self.ax.set_xlabel("Time (min)")
            self.ax.set_xlim(left=0, right=90)
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=1500)
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.fig.canvas.set_window_title("")
            # TODO: this plt stuff can probably go elsewhere
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

    def pickle_plot(self, to_plot):
        path = self.parent.parent.main.savepath.get()
        with open(os.path.join(path, 'plot.plt'), 'wb') as p:
            pickle.dump(to_plot, p)

    def unpickle_plot(self):
        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data to plot:",
            filetypes=[("Plot settings", "*.plt")]
            )
        with open(fil, 'rb') as p:
            to_plot = pickle.load(p)

        x = list(enumerate(to_plot))
        print(x)
        print(x[0])
        print(x[0][1])
        print(x[0][1][1])
