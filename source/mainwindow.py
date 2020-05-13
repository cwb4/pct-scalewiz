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
import serial.tools.list_ports
# from serial import SerialException
import sys  # handling file paths
import tkinter as tk  # GUI
from tkinter import ttk, scrolledtext


from experiment import Experiment
# from experiment_ import Experiment
from menubar import MenuBar


class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.core = parent
        self.config = self.core.config

        self.plotpsi = tk.StringVar()
        self.plotpsi.set(self.config.get('test settings', 'default pump'))
        self.project = os.path.normpath(
            self.config.get('test settings', 'project folder',
            fallback=os.getcwd()
            )
        )

        try:
            p = self.project.split('\\')
            self.title = p[-2] + " - " + p[-1]
        except IndexError:
            self.title=os.getcwd()
        self.winfo_toplevel().title(self.title)

        self.plotstyle = self.config.get('plot settings', 'default style')

        self.build_window()
        self.find_coms()

    def build_window(self) -> None:
        """Make all the tkinter widgets"""

        MenuBar(self)
        # build the main frame
        self.tstfrm = tk.Frame(self.core)
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Test parameters")
        # this spacing is to avoid using multiple labels
        self.outfrm = tk.LabelFrame(self.tstfrm,
            text="Elapsed,            Pump1,             Pump2")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Test controls")

        # define the self.entfrm entries
        self.port1 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify='center'
            )
        self.port2 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify='center'
            )
        self.chem = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify='center'
            )
        self.chem.focus_set()  # move the cursor here for convenience
        self.conc = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify='center'
            )
        self.strtbtn = ttk.Button(
            master=self.entfrm,
            text="Start",
            command= lambda: self.init_test()
            )

        # grid entry labels into self.entfrm
        self.comlbl = ttk.Label(master=self.entfrm, text="COM ports:")
        self.comlbl.grid(row=0, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Chemical:",
            anchor='e'
            ).grid(row=3, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Concentration:",
            anchor='e'
            ).grid(row=4, sticky=tk.E)

        # widget bindings for user convenience
        self.conc.bind("<Return>", lambda _: self.init_test())
        self.comlbl.bind("<Button-1>", lambda _: self.find_coms())

        # grid entries into self.entfrm
        self.port1.grid(row=0, column=1, sticky=tk.E, padx=(0,3))
        self.port2.grid(row=0, column=2, sticky=tk.W, padx=(3,0))
        self.chem.grid(row=3, column=1, columnspan=2, pady=1)
        self.conc.grid(row=4, column=1, columnspan=2, pady=1)
        self.strtbtn.grid(row=5, column=1, columnspan=2, pady=1)
        cols = self.entfrm.grid_size()[0]
        for col in range(cols):
            self.entfrm.grid_columnconfigure(col, weight=1)

        self.dataout = tk.scrolledtext.ScrolledText(
            master=self.outfrm,
            width=45,
            height=12,
            state='disabled'
        )

        self.dataout.pack(fill=tk.BOTH)
        if self.project is os.getcwd():
            self.to_log("Click 'Set project folder' to choose where",
            "files will be saved"
            )

        # build self.cmdfrm 4x3 grid
        self.runbtn = ttk.Button(
            master=self.cmdfrm,
            text="Run",
            command=lambda: self.test.run_test(),
            width=15
        )
        self.endbtn = ttk.Button(
            master=self.cmdfrm,
            text="End",
            command=lambda: self.test.end_test(),
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
            text=" "
        )
        if self.config.getboolean('plot settings', 'show style options'):
            self.pltfrm.configure(text=(f"Style: {self.plotstyle}"))

        # matplotlib objects
        self.fig, self.ax = plt.subplots(figsize=(7.5, 4), dpi=100)
        plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        # TODO: explicitly clarify some of these args
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.pltfrm)
        toolbar = NavigationToolbar2Tk(self.canvas, self.pltfrm)
        toolbar.update()
        self.canvas.get_tk_widget().pack()
        interval = self.config.getint('test settings', 'interval seconds')*1000
        self.ani = FuncAnimation(self.fig, self.animate, interval=interval)

        # grid stuff into self.tstfrm
        self.entfrm.grid(row=0, column=0, sticky=tk.NSEW, pady=2)
        self.pltfrm.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW, padx=2)
        self.outfrm.grid(row=1, column=0, sticky=tk.NSEW, pady=2)
        self.cmdfrm.grid(row=2, column=0, sticky=tk.NSEW, pady=2)
        self.tstfrm.grid(padx=3)

    def find_coms(self) -> None:
        """Looks for COM ports and disables the controls if two aren't found"""

        print("Finding COM ports")
        list = serial.tools.list_ports.comports()
        useports = [i.device for i in list]
        if len(useports) < 2:
            self.to_log("Not enough COM ports found...",
                        "Click 'COM ports:' to try again.")
            useports = ["??", "??"]

        self.port1.delete(0, tk.END)
        self.port2.delete(0, tk.END)
        self.port1.insert(0, useports[0])
        self.port2.insert(0, useports[1])

        if "?" in self.port1.get()  or "?" in self.port2.get():
            print("Disabling start button")
            self.strtbtn['state'] = ['disable']
        else:
            print(f"Successfully connected to COM ports {useports}")
            print("Enabling start button")
            self.strtbtn['state'] = ['enable']

    def init_test(self) -> None:
        """Scrape form for user input, then init an Experiment object"""

        print("Initializing a new Experiment")
        params = {
            'port1': self.port1.get().strip(),
            'port2': self.port2.get().strip(),
            'timelimit': self.config.getint('test settings', 'time limit minutes'),
            'failpsi': self.config.getint('test settings', 'fail psi'),
            'chem': self.chem.get().strip().replace(' ', '_'),
            'conc': self.conc.get().strip().replace(' ', '_')
        }
        self.test = Experiment(self, **params)

    def to_log(self, *msgs) -> None:
        """Logs a message to the Text widget in MainWindow's outfrm"""

        for msg in msgs:
            # print(msg)
            self.dataout['state'] = 'normal'
            self.dataout.insert('end', f"{msg}" + "\n")
            self.dataout['state'] = 'disabled'
            self.dataout.see('end')

    def animate(self, i):
        """The animation function for the current test's data"""

        try:
            data = read_csv(self.test.outpath)
        # maybe we didn't start running a test yet
        except (FileNotFoundError, AttributeError):
            data = DataFrame(data={'Minutes': [0], 'PSI 1': [0], 'PSI 2': [0]})

        # TODO: this plt stuff can probably go elsewhere
        plt.rcParams.update(plt.rcParamsDefault)  # refresh the style
        # plt.rcParams['axes.xmargin'] = 0.
        # https://stackoverflow.com/questions/42895216
        with plt.style.context(self.plotstyle):
            self.ax.clear()
            self.ax.set_xlabel("Time (min)")
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=self.config.getint('test settings', 'fail psi'))
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.set_xlim((0, None), auto=True)
            self.ax.margins(0)

            y = data[self.plotpsi.get()]
            x = data['Minutes']
            if self.chem.get() == "" and self.conc.get() == "":
                label = " "
            else:
                label = f"{self.chem.get().strip()} {self.conc.get().strip()}"
            self.ax.plot(x, y, label=label)

            self.ax.grid(color='darkgrey', alpha=0.65, linestyle='-')
            self.ax.set_facecolor('w')
            self.ax.legend(loc=0)
