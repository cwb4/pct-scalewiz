"""The main window of the application.
  - imports then creates an instance of MenuBar
  - has some tkinter widgets for user input / data visualization
"""


import csv  # logging the data
from datetime import datetime  # logging the data
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
from pandas import DataFrame, read_csv  # reading data from csv
import os  # handling file paths
import serial  # talking to the pumps
import sys  # handling file paths
import tkinter as tk  # GUI
from tkinter import ttk
import time  # sleeping
from winsound import Beep  # beeping when the test ends

from experiment import Experiment
from menubar import MenuBar


class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.plotpsi = tk.StringVar()
        self.plotstyle = tk.StringVar()
        self.plotpsi.set('PSI 2')
        self.plotstyle.set('seaborn-colorblind')
        self.build_window()
        self.findcoms()

    def build_window(self) -> None:
        """Make all the tkinter widgets"""
        self.menu = MenuBar(self)
        # build the main frame
        self.tstfrm = tk.Frame(self)
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Test parameters")
        # this spacing is to avoid using multiple labels
        self.outfrm = tk.LabelFrame(self.tstfrm,
            text="Elapsed,            Pump1,             Pump2")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Test controls")

        # define the self.entfrm entries
        self.p1 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify=tk.CENTER
            )
        self.p2 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify=tk.CENTER
            )
        self.tl = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.fp = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.ch = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.ch.focus_set()  # move the cursor here for convenience
        self.co = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.strtbtn = ttk.Button(
            master=self.entfrm,
            text="Start",
            command=self.init_test
            )

        # default values for convenience (maybe store in config file instead)
        self.tl.insert(0, '90')
        self.fp.insert(0, '1500')

        # grid entry labels into self.entfrm
        self.comlbl = ttk.Label(master=self.entfrm, text="COM ports:")
        self.comlbl.grid(row=0, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Time limit (min):"
            ).grid(row=1, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Failing pressure (psi):"
            ).grid(row=2, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Chemical:"
            ).grid(row=3, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Concentration:"
            ).grid(row=4, sticky=tk.E)

        # widget bindings for user convenience
        self.co.bind("<Return>", self.init_test)
        self.comlbl.bind("<Button-1>", lambda _: self.findcoms())

        # grid entries into self.entfrm
        self.p1.grid(row=0, column=1, sticky=tk.E, padx=(9, 1))
        self.p2.grid(row=0, column=2, sticky=tk.W, padx=(5, 3))
        self.tl.grid(row=1, column=1, columnspan=3, pady=1)
        self.fp.grid(row=2, column=1, columnspan=3, pady=1)
        self.ch.grid(row=3, column=1, columnspan=3, pady=1)
        self.co.grid(row=4, column=1, columnspan=3, pady=1)
        self.strtbtn.grid(row=5, column=1, columnspan=2, pady=1)
        cols = self.entfrm.grid_size()
        for col in range(cols[0]):
            self.entfrm.grid_columnconfigure(col, weight=1)

        # build self.outfrm packed
        scrollbar = tk.Scrollbar(self.outfrm)
        self.dataout = tk.Text(
            master=self.outfrm,
            width=39,
            height=12,
            yscrollcommand=scrollbar.set,
            state='disabled'
            )
        # TODO: try calling tk.Scrollbar(self.outfrm) directly
        scrollbar.config(command=self.dataout.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dataout.pack(fill=tk.BOTH)

        # build self.cmdfrm 4x3 grid
        self.runbtn = ttk.Button(
            master=self.cmdfrm,
            text="Run",
            command=lambda: self.run_test(),
            width=15
            )
        self.endbtn = ttk.Button(
            master=self.cmdfrm,
            text="End",
            command=lambda: self.end_test(),
            width=15
            )
        self.runbtn.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        self.endbtn.grid(row=1, column=2, padx=5, pady=2, sticky=tk.E)

        # a pair of Radiobuttons to choose which column of data to plot
        tk.Label(
            master=self.cmdfrm,
            text="Select data to plot:"
            ).grid(row=0, column=0, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="PSI 1",
            variable=self.plotpsi,
            value='PSI 1'
            ).grid(row=0, column=1, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="PSI 2",
            variable=self.plotpsi,
            value='PSI 2'
            ).grid(row=0, column=2, padx=5)

        # disable the controls to prevent starting test w/o parameters
        for child in self.cmdfrm.winfo_children():
            child.configure(state="disabled")

        # set up the plot area
        self.pltfrm = tk.LabelFrame(
            master=self.tstfrm,
            text=(f"Style: {self.plotstyle.get()}")
            )

        # matplotlib objects
        self.fig, self.ax = plt.subplots(figsize=(7.5, 4), dpi=100)
        plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        # TODO: explicitly clarify some of these args
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.pltfrm)
        toolbar = NavigationToolbar2Tk(self.canvas, self.pltfrm)
        toolbar.update()
        self.canvas.get_tk_widget().pack()
        self.ani = FuncAnimation(self.fig, self.animate, interval=1000)

        # grid stuff into self.tstfrm
        self.entfrm.grid(row=0, column=0, sticky=tk.NSEW, pady=2)
        self.pltfrm.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW, padx=2)
        self.outfrm.grid(row=1, column=0, sticky=tk.NSEW, pady=2)
        self.cmdfrm.grid(row=2, column=0, sticky=tk.NSEW, pady=2)
        self.tstfrm.grid(padx=3)

    def findcoms(self) -> None:
        """Looks for COM ports and disables the controls if two aren't found"""
        ports = ["COM" + str(i) for i in range(15)]
        useports = []
        for i in ports:
            if serial.Serial(i).is_open:
                useports.append(i)
                serial.Serial(i).close

        if len(useports) < 2:
            self.to_log("Not enough COM ports found...")
            self.to_log("Click 'COM ports:' to try again.")
            useports = ["??", "??"]

        try:
            self.p1.insert(0, useports[0])
            self.p2.insert(0, useports[1])

            if self.p1.get() == "??" or self.p2.get() == "??":
                self.strtbtn['state'] = ['disable']
            else:
                self.strtbtn['state'] = ['enable']
                # TODO: clean this up
        except IndexError:
            pass
        except AttributeError:
            pass

    def init_test(self) -> None:
        """init an Experiment object as an attribute of MainWindow"""
        self.test = Experiment(self)

    def to_log(self, msg) -> None:
        """Logs a message to the Text widget in MainWindow's outfrm"""
        self.dataout['state'] = 'normal'
        self.dataout.insert('end', f"{msg}" + "\n")
        self.dataout['state'] = 'disabled'
        self.dataout.see('end')

    def animate(self, i):
        """The animation function for the current test's data"""
        try:
            data = read_csv(os.path.join(self.savepath.get(), self.outfile))
        except FileNotFoundError as e:
            data = DataFrame(data={'Minutes': [0], 'PSI 1': [0], 'PSI 2': [0]})

        # TODO: this plt stuff can probably go elsewhere
        plt.rcParams.update(plt.rcParamsDefault)  # refresh the style
        # https://stackoverflow.com/questions/42895216
        with plt.style.context(self.plotstyle.get()):
            self.pltfrm.config(text=("Style: " + self.plotstyle.get()))
            self.ax.clear()
            self.ax.set_xlabel("Time (min)")
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=self.failpsi.get())
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.set_xlim(left=0, right=self.timelimit.get())

            y = data[self.plotpsi.get()]
            x = data['Minutes']
            self.ax.plot(x, y, label=(f"{self.chem.get()}_{self.conc.get()}"))

            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.ax.legend(loc=0)
