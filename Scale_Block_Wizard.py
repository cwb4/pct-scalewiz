
import tkinter as tk
from tkinter import ttk, filedialog
from concurrent.futures import ThreadPoolExecutor
import os, sys # handling file paths
import serial # talking to the pumps
import csv # logging the data
import time # sleeping
from datetime import datetime # logging the data
from winsound import Beep # beeping when the test ends
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
import pickle

class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # define test parameters
        self.port1 = tk.StringVar() # COM port for pump1
        self.port2 = tk.StringVar() # COM port for pump2
        self.timelimit = tk.DoubleVar()
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
        self.tstfrm = tk.Frame(self.parent)
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Test parameters")
        self.outfrm = tk.LabelFrame(self.tstfrm,
         text="Elapsed,            Pump1,             Pump2")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Test controls")

        # define the self.entfrm entries
        self.p1 = ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.port1,
            justify=tk.CENTER
            )
        self.p2 = ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.port2,
            justify=tk.CENTER
            )
        self.tl = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            textvariable=self.timelimit
            )
        self.fp = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            textvariable=self.failpsi
            )
        self.ch = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            textvariable=self.chem
            )
        self.co = ttk.Entry(
            master=self.entfrm,
            width=30,
            justify=tk.CENTER,
            textvariable=self.conc
            )
        self.strtbtn = ttk.Button(
            master=self.entfrm,
            text="Start",
            command=self.init_test
            )

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

        # grid entries into self.entfrm
        self.p1.grid(row=0, column=1, sticky=tk.E,padx=(11, 1))
        self.p2.grid(row=0, column=2, sticky=tk.W,padx=(5, 1))
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

        # build self.cmdfrm 4x3 GRID
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
        tk.Label(
            master=self.cmdfrm,
            text="Select data to plot:"
            ).grid(row=0, column=0, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="PSI 1",
            variable=self.plotpsi,
            value='PSI 1'
            ).grid(row = 0, column = 1, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="PSI 2",
            variable=self.plotpsi,
            value='PSI 2'
            ).grid(row = 0, column = 2, padx=5)

        if self.paused:
            for child in self.cmdfrm.winfo_children():
                child.configure(state="disabled")

        self.pltfrm = tk.LabelFrame(
            master=self.tstfrm,
            text=("Style: " + self.plotstyle.get())
            )

        self.fig, self.ax = plt.subplots(figsize=(7.5, 4), dpi=100)
        plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        #plt.tight_layout()
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

        # widget bindings
        self.co.bind("<Return>", self.init_test)
         # TODO: there has to be a more concise way
        self.comlbl.bind("<Button-1>", lambda _: self.findcoms())

        self.tstfrm.grid(padx=3)
        self.findcoms()
        self.ch.focus_set()

    def findcoms(self):
              #find the com ports
            self.to_log("Finding COM ports ...")
            ports = ["COM" + str(i) for i in range(15)]
            useports = []
            for i in ports:
                try:
                    if serial.Serial(i).is_open:
                        self.to_log(f"Found an open port at {i}")
                        useports.append(i)
                        serial.Serial(i).close
                except serial.SerialException:
                    pass
            if useports == []:
                self.to_log("No COM ports found ...")
                self.to_log("Click the 'COM ports:' label above to try again.")
                useports = ["??", "??"]
            try:
                self.port1.set(useports[0])
                self.port2.set(useports[1])
                if self.port1.get() == "??" or self.port2.get() == "??":
                    self.strtbtn['state']=['disable']
                else:
                    self.strtbtn['state']=['enable']
            except IndexError:
                pass
            except AttributeError:
                pass

    def init_test(self):
        self.paused = True
        self.port1.set(self.p1.get())
        self.port2.set(self.p2.get())
        self.timelimit.set(self.tl.get())
        self.failpsi.set(self.fp.get())
        self.chem.set(self.ch.get())
        self.conc.set(self.co.get())

        self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        self.psi1, self.psi2, self.elapsed = 0, 0, 0
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
        starttime = datetime.now()
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
            self.elapsed = (datetime.now() -  starttime).seconds

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
        with plt.style.context(self.plotstyle.get()):
            self.pltfrm.config(text=("Style: " + self.plotstyle.get()))
            self.ax.clear()
            self.ax.set_xlabel("Time (min)")
            self.ax.set_ylabel("Pressure (psi)")
            self.ax.set_ylim(top=self.failpsi.get())
            self.ax.yaxis.set_major_locator(MultipleLocator(100))
            self.ax.set_xlim(left=0,right=self.timelimit.get())

            y = data[self.plotpsi.get()]
            x = data['Minutes']
            self.ax.plot(x,y,
             label=("{0} {1}".format(self.chem.get(), self.conc.get())))
            self.ax.grid(color='grey', alpha=0.3)
            self.ax.set_facecolor('w')
            self.ax.legend(loc=0)

class MenuBar(tk.Frame):
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
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.build()

    def build(self):
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self, tearoff=0)
        self.filemenu.add_command(
            label=self.parent.main.savepath.get(),
            command=self.askdir
            )
        self.pltmenu = tk.Menu(master=self, tearoff=0)
        self.pltstylmenu = tk.Menu(master=self, tearoff=1)
        for style in MenuBar.styles:
            self.pltstylmenu.add_command(
                label=style,
                command=lambda s=style: (self.parent.main.plotstyle.set(s))
                )

        self.pltmenu.add_command(label="Make new plot", command=self.new_plot)
        self.pltmenu.add_cascade(label="Set plot style", menu=self.pltstylmenu)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Plot", menu=self.pltmenu)
        self.parent.winfo_toplevel().config(menu=self.menubar)

    def askdir(self):
        out = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select data output directory:"
            )

        if out == "":
            pass
        else:
            self.parent.main.savepath.set(out)
            p = self.parent.main.savepath.get().split('/')
            pp = p[-2] + " - " + p[-1]
            self.filemenu.entryconfig(index=1, label=pp)
            self.parent.main.project.set(pp)
            self.parent.winfo_toplevel().title(self.parent.main.project.get())
            # self.parent.root.title(self.parent.project.get())

    def new_plot(self):
        self.parent.plotter = Plotter(self)

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


class SeriesEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.plotpump = tk.StringVar()
        self.plotpump.set("PSI 2")
        self.build()

    def build(self):
        self.path = ttk.Entry(self, width=20)
        self.path.bind("<Button-1>", self.askfil)
        self.path.grid(row=0, column=0, padx=2, pady=1)

        self.title = ttk.Entry(self, width=20)
        self.title.grid(row=0, column=1, padx=2, pady=1)

        tk.Radiobutton(
            master=self,
            text="PSI 1",
            variable=self.plotpump,
            value='PSI 1'
            ).grid(row=0, column=2, padx=2, pady=1)

        tk.Radiobutton(
            master=self,
            text="PSI 2",
            variable=self.plotpump,
            value='PSI 2'
            ).grid(row=0, column=3, padx=2, pady=1)

        ttk.Button(
            master=self,
            text="Remove",
            command=self.clear_ents
            ).grid(row=0, column=4, padx=2, pady=2)

    def askfil(self, event):
        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data output directory:",
            filetypes=[("CSV files", "*.csv")]
            )

        if not fil == "":
            event.widget.delete(0, tk.END)
            event.widget.insert(0, fil)
            event.widget.after(50, event.widget.xview_moveto, 1)
            event.widget.after(50, lambda: self.title.focus_set())
        # NOTE: :  for some reason this only fires if postponed
        # https://stackoverflow.com/questions/29334544/

    def clear_ents(self):
        self.path.delete(0, tk.END)
        self.title.delete(0, tk.END)

class ScaleWiz(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = MainWindow(self)
        self.menu = MenuBar(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=False)

    def close_ports():  # attempts to close all open ports, just in case
        import serial
        ports = ["COM" + str(i) for i in range(15)]
        for i in ports:
            try:
                if serial.Serial(i).is_open:
                    print(f"Closing {i}")
                    serial.Serial(i).close
            except serial.SerialException:
                pass
        print("Destroying root")
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", close_ports)
    root.mainloop()
