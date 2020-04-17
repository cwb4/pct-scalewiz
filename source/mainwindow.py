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
from tkinter import ttk


from experiment import Experiment
from menubar import MenuBar


class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.plotpsi = tk.StringVar()
        self.plotpsi.set('PSI 2')
        self.project = os.getcwd()
        self.plotstyle = ('bmh')

        self.build_window()
        self.findcoms()

    def build_window(self) -> None:
        """Make all the tkinter widgets"""
        self.menu = MenuBar(self)
        # build the main frame
        self.tstfrm = tk.Frame(self.parent)
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Test parameters")
        # this spacing is to avoid using multiple labels
        self.outfrm = tk.LabelFrame(self.tstfrm,
            text="Elapsed,            Pump1,             Pump2")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Test controls")

        # define the self.entfrm entries
        self.port1 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify=tk.CENTER
            )
        self.port2 = ttk.Entry(
            master=self.entfrm,
            width=14,
            justify=tk.CENTER
            )
        self.timelim = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.failpsi = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.chem = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.chem.focus_set()  # move the cursor here for convenience
        self.conc = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            )
        self.strtbtn = ttk.Button(
            master=self.entfrm,
            text="Start",
            command= lambda: self.init_test()
            )

        # default values for convenience (maybe store in config file instead)
        self.timelim.insert(0, '90')
        self.failpsi.insert(0, '1500')

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
        self.conc.bind("<Return>", lambda _: self.init_test())
        self.comlbl.bind("<Button-1>", lambda _: self.findcoms())

        # grid entries into self.entfrm
        self.port1.grid(row=0, column=1, sticky=tk.E, padx=(17, 1))
        self.port2.grid(row=0, column=2, sticky=tk.W, padx=(5, 3))
        self.timelim.grid(row=1, column=1, columnspan=3, pady=1)
        self.failpsi.grid(row=2, column=1, columnspan=3, pady=1)
        self.chem.grid(row=3, column=1, columnspan=3, pady=1)
        self.conc.grid(row=4, column=1, columnspan=3, pady=1)
        self.strtbtn.grid(row=5, column=1, columnspan=2, pady=1)
        cols = self.entfrm.grid_size()
        for col in range(cols[0]):
            self.entfrm.grid_columnconfigure(col, weight=1)

        # build self.outfrm packed
        scrollbar = tk.Scrollbar(self.outfrm)
        self.dataout = tk.Text(
            master=self.outfrm,
            width=45,
            height=12,
            yscrollcommand=scrollbar.set,
            state='disabled'
            )
        # TODO: try calling tk.Scrollbar(self.outfrm) directly
        scrollbar.config(command=self.dataout.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dataout.pack(fill=tk.BOTH)
        self.to_log("Click 'Set project folder' to choose where")
        self.to_log("files will be saved")

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
            text=(f"Style: {self.plotstyle}")
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
        list = serial.tools.list_ports.comports()
        useports = [i.device for i in list]
        # useports = [port for port in ports if serial.Serial(port).is_open]

        # for i in ports:
        #     try:
        #         if serial.Serial(i).is_open:
        #             useports.append(i)
        #             serial.Serial(i).close
        #     except SerialException:
        #         pass

        if len(useports) < 2:
            self.to_log("Not enough COM ports found...")
            self.to_log("Click 'COM ports:' to try again.")
            useports = ["??", "??"]

        try:
            self.port1.delete(0, tk.END)
            self.port2.delete(0, tk.END)
            self.port1.insert(0, useports[0])
            self.port2.insert(0, useports[1])

            if "?" in self.port1.get()  or "?" in self.port2.get():
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
            data = read_csv(self.test.outpath)
        # maybe we didn't start running a test yet
        except (FileNotFoundError, AttributeError):
            data = DataFrame(data={'Minutes': [0], 'PSI 1': [0], 'PSI 2': [0]})

        # TODO: this plt stuff can probably go elsewhere
        plt.rcParams.update(plt.rcParamsDefault)  # refresh the style
        # https://stackoverflow.com/questions/42895216
        with plt.style.context(self.plotstyle):
            self.pltfrm.config(text=f"Style: {self.plotstyle}")
            self.ax.clear()
            self.ax.set_xlabel("Time (min)")
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=int(self.failpsi.get()))
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.set_xlim(left=0,)
            # right=int(self.timelim.get()))

            y = data[self.plotpsi.get()]
            x = data['Minutes']
            if self.chem.get() == "" and self.conc.get() == "":
                 datalabel = " "
            else: datalabel = f"{self.chem.get()} {self.conc.get()}"
            self.ax.plot(x, y, label=datalabel)

            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.ax.legend(loc=0)
