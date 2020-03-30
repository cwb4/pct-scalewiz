# -*- coding: utf-8 -*-
""" The main window for accepting user inputs
Todo:
    * try calling scrollbar directly in build_window
    * cleaner bindings for init_test calls in build_window
    * change taking reading method to calculate elapsed from OS time
"""

import tkinter as tk
from tkinter import ttk
import os, sys # handling file paths
import serial # talking to the pumps
import csv # logging the data
import time # logging data / talking to the pumps
from winsound import Beep # beeping when the test ends
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator

class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # define test parameters
        self.port1 = tk.StringVar() # COM port for pump1
        self.port2 = tk.StringVar() # COM port for pump2
        self.timelimit = tk.IntVar()
        self.failpsi = tk.IntVar()
        self.chem = tk.StringVar()
        self.conc = tk.StringVar()
        self.savepath = tk.StringVar() # output directory
        self.project = tk.StringVar() # used for window title
        self.plotpsi = tk.StringVar() # for which pump's data to plot
        self.plotstyle = tk.StringVar()

        # set initial
        self.paused = True
        self.timelimit.set(90)
        self.failpsi.set(1500)
        self.savepath.set(os.getcwd())
        self.plotpsi.set('PSI 2')
        self.plotstyle.set('seaborn-colorblind')
        self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        self.build_window()

    def build_window(self):
        # build the main frame
        self.tstfrm = tk.Frame(self.parent) #put everything here, pack at the end
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Test parameters")
        self.outfrm = tk.LabelFrame(self.tstfrm,
         text="Elapsed,            Pump1,             Pump2")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Test controls")

        # define the self.entfrm entries
        self.p1 = ttk.Entry(self.entfrm,
         width=14, textvariable=self.port1, justify=tk.CENTER)
        self.p2 = ttk.Entry(self.entfrm,
         width=14, textvariable=self.port2, justify=tk.CENTER)
        self.tl = ttk.Entry(self.entfrm,
         width=30, justify=tk.CENTER, textvariable=self.timelimit)
        self.fp = ttk.Entry(self.entfrm,
         width=30, justify=tk.CENTER, textvariable=self.failpsi)
        self.ch = ttk.Entry(self.entfrm,
         width=30, justify=tk.CENTER, textvariable=self.chem)
        self.co = ttk.Entry(self.entfrm,
         width=30, justify=tk.CENTER, textvariable=self.conc)
        self.strtbtn = ttk.Button(self.entfrm, text="Start",
         command= lambda: self.init_test(self.p1.get(), self.p2.get(),
         self.tl.get(), self.fp.get(), self.ch.get(), self.co.get()))

        # grid entry labels into self.entfrm
        self.comlbl = ttk.Label(self.entfrm, text="COM ports:")
        self.comlbl.grid(row=0, sticky=tk.E)
        ttk.Label(self.entfrm,
         text="Time limit (min):").grid(row=1, sticky=tk.E)
        ttk.Label(self.entfrm,
         text="Failing pressure (psi):").grid(row=2, sticky=tk.E)
        ttk.Label(self.entfrm,
         text="Chemical:").grid(row=3, sticky=tk.E)
        ttk.Label(self.entfrm,
         text="Concentration:").grid(row=4, sticky=tk.E)

        # grid entries into self.entfrm
        self.p1.grid(row=0, column=1, sticky=tk.E,padx=(11,1))
        self.p2.grid(row=0, column=2, sticky=tk.W,padx=(5,1))
        self.tl.grid(row=1, column=1, columnspan=3, pady=1)
        self.fp.grid(row=2, column=1, columnspan=3, pady=1)
        self.ch.grid(row=3, column=1, columnspan=3, pady=1)
        self.co.grid(row=4, column=1, columnspan=3, pady=1)
        self.strtbtn.grid(row=5, column=1, columnspan=2, pady=1)
        cols = self.entfrm.grid_size()
        for col in range(cols[0]):
            self.entfrm.grid_columnconfigure(col, weight=1)

        #build self.outfrm PACK
        scrollbar = tk.Scrollbar(self.outfrm)
        self.dataout = tk.Text(self.outfrm,
         width=39, height=12, yscrollcommand=scrollbar.set, state='disabled')
         # TODO: try calling tk.Scrollbar(self.outfrm) directly
        scrollbar.config(command=self.dataout.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dataout.pack(fill=tk.BOTH)

        # build self.cmdfrm 4x3 GRID
        self.runbtn = ttk.Button(self.cmdfrm,
         text="Run", command=lambda:self.run_test(), width=15)
        self.paubtn = ttk.Button(self.cmdfrm,
         text="Pause/Resume", command =lambda:self.pause_test(), width=15)
        self.endbtn = ttk.Button(self.cmdfrm,
         text="End", command=lambda:self.end_test(), width=15)
        self.runbtn.grid(row = 0, column=0, padx=5, sticky=tk.W)
        self.paubtn.grid(row = 0, column=1, padx=15)
        self.endbtn.grid(row = 0, column=2, padx=5, sticky=tk.E)
        tk.Label(self.cmdfrm,
         text="Select data to plot:").grid(row=3, column=0, padx=5)
        tk.Radiobutton(self.cmdfrm, text="PSI 1",
         variable=self.plotpsi, value='PSI 1').grid(row = 3, column = 1, padx=5)
        tk.Radiobutton(self.cmdfrm, text="PSI 2",
         variable=self.plotpsi, value='PSI 2').grid(row = 3, column = 2, padx=5)

        if self.paused:
            for child in self.cmdfrm.winfo_children():
                child.configure(state="disabled")

        self.pltfrm = tk.LabelFrame(self.tstfrm, text=("Style: " +self.plotstyle.get()))
        self.fig, self.ax = plt.subplots(figsize=(7.5,4), dpi=100)
        plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        #plt.tight_layout()
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

        # widget bindings
        self.co.bind("<Return>", lambda _: self.init_test(self.p1.get(),
         self.p2.get(), self.tl.get(), self.fp.get(),
         self.ch.get(), self.co.get()))
         # TODO: there has to be a more concise way
        self.comlbl.bind("<Button-1>", lambda _: self.findcoms())

        self.tstfrm.grid(padx=3)
        self.findcoms()
        self.ch.focus_set()

    def findcoms(self):
              #find the com ports
            print("Finding COM ports ...")
            ports = ["COM" + str(i) for i in range(15)]
            useports = []
            for i in ports:
                try:
                    if serial.Serial(i).is_open:
                        print(f"Found an open port at {i}")
                        useports.append(i)
                        serial.Serial(i).close
                except serial.SerialException:
                    pass
            if useports == []:
                print("No COM ports found")
                useports = ["??", "??"]
            try:
                self.port1.set(useports[0])
                self.port2.set(useports[1])
                if self.port1.get() == "??" or self.port2.get() =="??":
                    self.strtbtn['state']=['disable']
                else: self.strtbtn['state']=['enable']
            except IndexError:
                pass
            except AttributeError:
                pass

    def init_test(self, pump1, pump2, timelimit, failpsi, chem, conc):
        self.paused = True
        self.port1.set(pump1)
        self.port2.set(pump2)
        self.timelimit.set(timelimit)
        self.failpsi.set(failpsi)
        self.chem.set(chem)
        self.conc.set(conc)
        self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        self.psi1, self.psi2, self.elapsed = 0,0,0
        # the timeout values are an alternative to using TextIOWrapper
        self.pump1 = serial.Serial(self.port1.get(), timeout=0.01)
        print(f"Opened a port at {self.port1.get()}")
        self.pump2 = serial.Serial(self.port2.get(), timeout=0.01)
        print(f"Opened a port at {self.port2.get()}")

        # set up output file
        print("Creating output file at",
         os.path.join(self.savepath.get(), self.outfile))
        with open(os.path.join(self.savepath.get(), self.outfile),"w") as f:
                csv.writer(f, delimiter=',').writerow(
                ["Timestamp", "Seconds", "Minutes", "PSI 1", "PSI 2"])
        for child in self.entfrm.winfo_children():
            child.configure(state="disabled")
        for child in self.cmdfrm.winfo_children():
            child.configure(state="normal")

    def to_log(self, msg):
        self.dataout['state'] = 'normal'
        self.dataout.insert('end', str(msg) +"\n")
        self.dataout['state'] = 'disabled'
        self.dataout.see('end')

    def pause_test(self):
        if self.paused == True:
            self.pump1.write('ru'.encode())
            self.pump2.write('ru'.encode())
            self.to_log("Resuming test ...")
            time.sleep(3) # let the pumps warm up before recording data
            self.parent.thread_pool_executor.submit(self.take_reading)
            self.paused = False

        elif self.paused == False:
            self.to_log("Pausing test ...")
            self.pump1.write('st'.encode())
            self.pump2.write('st'.encode())
            self.paused = True

    def end_test(self):
        self.paused = True
        self.pump1.write('st'.encode()), self.pump1.close()
        self.pump2.write('st'.encode()), self.pump2.close()
        msg = "The test finished in {0:.2f} minutes ...".format(self.elapsed/60)
        self.to_log(msg)
        for child in self.entfrm.winfo_children():
            child.configure(state="normal")
        for child in self.cmdfrm.winfo_children():
            child.configure(state="disabled")

    def run_test(self):
        if self.paused == True:
            self.pump1.write('ru'.encode())
            self.pump2.write('ru'.encode())
            self.paused = False
            time.sleep(3) # let the pumps warm up before we start recording data
            self.parent.thread_pool_executor.submit(self.take_reading)

    def take_reading(self): # loop to be handled by threadpool
        # this is way too long of a line
        while (
         (self.psi1 < self.failpsi.get() or self.psi2 < self.failpsi.get())
         and self.elapsed < self.timelimit.get()*60
         and self.paused == False
         ):
            rn = time.strftime("%I:%M:%S", time.localtime())
            self.pump1.write("cc".encode())
            self.pump2.write("cc".encode())
            time.sleep(0.1)
            self.psi1 = int(self.pump1.readline().decode().split(',')[1])
            self.psi2 = int(self.pump2.readline().decode().split(',')[1])
            thisdata=[rn, self.elapsed,'{0:.2f}'.format(self.elapsed/60),
             self.psi1, self.psi2]
            with open((os.path.join(self.savepath.get(), self.outfile)),"a",
             newline='') as f:
                csv.writer(f,delimiter=',').writerow(thisdata)
            logmsg = ("{0:.2f} min, {1} psi, {2} psi".format(self.elapsed/60,
             str(self.psi1), str(self.psi2)))
            self.to_log(logmsg)
            time.sleep(0.9)
            self.elapsed += 1

        if self.paused == False:
            self.end_test()
            for i in range(3):
                Beep(750, 500)
                time.sleep(0.5)

    def animate(self, i):
        try:
            data = pd.read_csv(os.path.join(self.savepath.get(), self.outfile))
        except FileNotFoundError as e:
            data = pd.DataFrame(data={'Minutes':[0], 'PSI 1':[0], 'PSI 2':[0]})

        # TODO: this plt stuff can probably go elsewhere
        plt.rcParams.update(plt.rcParamsDefault) # refresh the style
        # https://stackoverflow.com/questions/42895216
        plt.style.use(self.plotstyle.get())
        self.pltfrm.config(text=("Style: " + self.plotstyle.get()))
        self.ax.clear()
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Pressure (psi)")
        self.ax.set_ylim(top=1500)
        self.ax.yaxis.set_major_locator(MultipleLocator(100))
        self.ax.set_xlim(left=0,right=90)

        y = data[self.plotpsi.get()]
        x = data['Minutes']
        self.ax.plot(x,y,
         label=("{0} {1}".format(self.chem.get(), self.conc.get())))
        self.ax.grid(color='grey', alpha=0.3)
        self.ax.set_facecolor('w')
        self.ax.legend(loc=0)
