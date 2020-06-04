"""The main window of the application.

- imports then creates an instance of MenuBar
- has some tkinter widgets for user input / data visualization
"""

import os  # handling file paths
import tkinter as tk  # GUI
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import font  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator
from pandas import DataFrame, read_csv  # reading data from csv
import serial  # talking to the pumps
import serial.tools.list_ports
from serial import SerialException

from experiment import Experiment
from menubar import MenuBar


class MainWindow(tk.Frame):
    """Main window for the application."""

    def __init__(self, parent, *args, **kwargs):
        """Initialize with the root as parent."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.core = parent
        self.core.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.parser = self.core.parser

        self.project = os.path.normpath(
            self.parser.get(
                'test settings',
                'project folder',
                fallback=os.getcwd()
            )
        )

        self.update_title()
        self.ports = []
        self.port1_val = tk.StringVar()
        self.port2_val = tk.StringVar()
        self.port1_val.trace('w', self.check_unique_port1)
        self.port2_val.trace('w', self.check_unique_port2)

        self.build_window()
        self.update_port_boxes()
        self.port1.set(self.ports[0])
        self.port2.set(self.ports[1])

    def build_window(self) -> None:
        """Make all the tkinter widgets."""
        MenuBar(self)
        bold_font = font.Font(font=font.nametofont("TkDefaultFont"))
        bold_font.config(weight='bold')

        # build the main frame
        self.tst_frm = tk.Frame(self.core)  # top level container
        # frame for parameter entries
        self.ent_frm = tk.LabelFrame(
            self.tst_frm,
            text="Test parameters",
            font=bold_font
        )
        # a frame for test controls
        self.cmd_frm = tk.LabelFrame(
            self.tst_frm,
            text="Test controls",
            font=bold_font
        )
        # define the self.ent_frm entries
        self.port1 = ttk.Combobox(
            self.ent_frm,
            values=self.ports,
            textvariable=self.port1_val,
            width=9,
            justify='center',
            state='readonly'
        )
        self.port2 = ttk.Combobox(
            self.ent_frm,
            values=self.ports,
            textvariable=self.port2_val,
            width=9,
            justify='center',
            state='readonly'
        )
        self.chem = ttk.Entry(
            self.ent_frm,
            width=25,
            justify='center'
        )
        self.conc = ttk.Entry(
            self.ent_frm,
            width=25,
            justify='center'
        )
        self.strt_btn = ttk.Button(
            self.ent_frm,
            text="Start",
            command=lambda: self.init_test()
        )
        # make entry labels for self.ent_frm
        com_lbl = ttk.Label(
            self.ent_frm,
            text="Device ports:",
        )
        chem_lbl = ttk.Label(
            self.ent_frm,
            text="Chemical:",
            anchor='e'
        )
        conc_lbl = ttk.Label(
            self.ent_frm,
            text="Concentration:",
            anchor='e'
        )

        # grid the labels
        com_lbl.grid(row=0, sticky=tk.E)
        chem_lbl.grid(row=3, sticky=tk.E)
        conc_lbl.grid(row=4, sticky=tk.E)

        # grid entries into self.ent_frm
        self.port1.grid(row=0, column=1, sticky=tk.E, padx=(0, 4), pady=1)
        self.port2.grid(row=0, column=2, sticky=tk.W, padx=(4, 0), pady=1)
        self.chem.grid(row=3, column=1, columnspan=2, pady=1)
        self.conc.grid(row=4, column=1, columnspan=2, pady=1)
        self.strt_btn.grid(row=5, column=1, columnspan=2, pady=1)
        cols = self.ent_frm.grid_size()[0]
        for col in range(cols):
            self.ent_frm.grid_columnconfigure(col, weight=1)

        # a frame for the output panel
        self.out_frm = tk.LabelFrame(
            self.tst_frm,
            # this spacing is to avoid using multiple labels
            text="Elapsed,            Pump1,             Pump2",
            font=bold_font
        )
        self.data_out = ScrolledText(
            master=self.out_frm,
            width=45,
            height=13,
            state='disabled',
            wrap='word'
        )

        self.data_out.pack()
        if self.project is os.getcwd():
            self.to_log(
                "Click 'Set project folder' to choose the output directory"
            )

        # build self.cmd_frm 4x3 grid
        self.run_btn = ttk.Button(
            master=self.cmd_frm,
            text="Run",
            command=lambda: self.test.run_test(),
            width=15
        )
        self.end_btn = ttk.Button(
            master=self.cmd_frm,
            text="End",
            command=lambda: self.end_test(),
            width=15
        )
        self.run_btn.grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.end_btn.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        cols = self.cmd_frm.grid_size()[0]
        for col in range(cols):
            self.cmd_frm.grid_columnconfigure(col, weight=1)

        tk.Label(
            master=self.cmd_frm,
            text="Select data to plot:"
        ).grid(row=0, column=0, padx=5, sticky='e')
        # combobox to choose which set of data to plot
        self.def_pump = ttk.Combobox(
            master=self.cmd_frm,
            values=["PSI 1", "PSI 2"],
            state='readonly',
            justify='center',
            background='white',
            width=13,
        )
        self.def_pump.set(self.parser.get('test settings', 'default pump'))

        self.def_pump.grid(row=0, column=1, padx=5, sticky='w')

        # set up the plot area
        self.plt_frm = tk.Frame(master=self.tst_frm)

        # matplotlib objects
        self.fig, self.axis = plt.subplots(figsize=(7.5, 4), dpi=100)
        plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plt_frm)
        self.canvas.get_tk_widget().pack(pady=(7, 0))
        interval = self.parser.getint('test settings', 'interval seconds') * 1000
        self.ani = FuncAnimation(self.fig, self.animate, interval=interval)

        # grid stuff into self.tst_frm
        self.ent_frm.grid(row=0, column=0, sticky='new')
        self.plt_frm.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.out_frm.grid(row=1, column=0, sticky='nsew')
        self.cmd_frm.grid(row=2, column=0, sticky='sew')
        self.tst_frm.grid(padx=3)

        # widget bindings
        self.chem.bind("<Return>", lambda _: self.conc.focus_set())
        self.conc.bind("<Return>", lambda _: self.init_test())
        com_lbl.bind("<Button-1>", lambda _: self.update_port_boxes())
        self.port1.bind("<Button-1>", lambda _: self.update_port_boxes())
        self.port2.bind("<Button-1>", lambda _: self.update_port_boxes())
        self.port1.bind("<FocusIn>", lambda _: self.tst_frm.focus_set())
        self.port2.bind("<FocusIn>", lambda _: self.tst_frm.focus_set())
        self.run_btn.bind('<Return>', lambda _: self.test.run_test())
        self.end_btn.bind('<Return>', lambda _: self.test.end_test())
        # move the cursor here for convenience
        self.chem.focus_set()
        # disable the controls to prevent starting test w/o parameters
        for widget in (self.run_btn, self.end_btn, self.def_pump):
            widget.configure(state="disabled")

    def find_coms(self) -> list:
        """Look for devices and returns a list of open ports."""
        print("Finding connected devices")
        ports = [i.device for i in serial.tools.list_ports.comports()]
        print(f"Found these devices: {ports}")
        if len(ports) < 2:
            self.to_log("Not enough devices found...",
                        "Click 'Device ports:' to try again.")
            ports = ["??", "??"]

        open_ports = []
        for port in ports:
            if port != "??":
                try:
                    device = serial.Serial(port)
                    device.close()
                    open_ports.append(port)
                except SerialException as error:
                    self.to_log(f"Could not connect to port {port}")
                    print(error)
                    open_ports.append("??")
            else:
                open_ports.append("??")
        print(f"Successfully connected to devices {open_ports}")
        return open_ports

    def update_port_boxes(self):
        """Update the device port Comboboxes."""
        self.ports = self.find_coms()
        self.port1.configure(values=self.ports)
        self.port2.configure(values=self.ports)

        # update the list, each can be selected only once
        if "?" in self.port1.get() or "?" in self.port2.get():
            print("Disabling start button")
            self.strt_btn.configure(state='disabled')
        else:
            self.data_out.configure(state='normal')
            self.data_out.delete(1.0, 'end')
            self.data_out.configure(state='normal')
            print("Enabling start button")
            self.strt_btn.configure(state='normal')

    def check_unique_port1(self, *args):
        """Make sure each selected port value is unique."""
        if self.port1_val.get() == self.port2_val.get():
            self.port2_val.set(self.ports[self.port2.current() - 1])

    def check_unique_port2(self, *args):
        """Make sure each selected port value is unique."""
        if self.port2_val.get() == self.port1_val.get():
            self.port1_val.set(self.ports[self.port1.current() - 1])

    def init_test(self) -> None:
        """Scrape form for user input, then init an Experiment object."""
        print("Initializing a new Experiment")
        params = {
            'port1': self.port1.get().strip(),
            'port2': self.port2.get().strip(),
            'timelimit': self.parser.getint(
                'test settings',
                'time limit minutes'
            ),
            'failpsi': self.parser.getint('test settings', 'fail psi'),
            'chem': self.chem.get().strip().replace(' ', '_'),
            'conc': self.conc.get().strip().replace(' ', '_')
        }
        self.test = Experiment(self, **params)
        self.run_btn.focus_set()

    def end_test(self):
        """Sets the test.running variable to False."""
        if hasattr(self, 'test'):
            self.test.running = False

    def to_log(self, *msgs) -> None:
        """Log a message to the Text widget in MainWindow's outfrm."""
        for msg in msgs:
            self.data_out['state'] = 'normal'
            self.data_out.insert('end', f"{msg}" + "\n")
            self.data_out['state'] = 'disabled'
            self.data_out.see('end')

    def animate(self, interval) -> None:
        """Call animation function for the current test's data."""
        try:
            data = read_csv(self.test.outpath)
        # maybe we didn't start running a test yet
        except (FileNotFoundError, AttributeError):
            data = DataFrame(data={'Minutes': [0], 'PSI 1': [0], 'PSI 2': [0]})

        with plt.style.context('bmh'):
            self.axis.clear()
            self.axis.set_xlabel("Time (min)")
            self.axis.set_ylabel("Pressure (psi)")
            self.axis.set_ylim(
                top=self.parser.getint(
                    'test settings',
                    'fail psi'
                )
            )
            self.axis.yaxis.set_major_locator(MultipleLocator(100))
            self.axis.set_xlim((0, None), auto=True)
            self.axis.margins(0)

            y_data = data[self.def_pump.get()]
            x_data = data['Minutes']
            if self.chem.get() == "" and self.conc.get() == "":
                label = " "
            else:
                label = f"{self.chem.get().strip()} {self.conc.get().strip()}"
            self.axis.plot(x_data, y_data, label=label)

            self.axis.grid(color='darkgrey', alpha=0.65, linestyle='-')
            self.axis.set_facecolor('w')
            self.axis.legend(loc=0)

    def update_title(self) -> None:
        """Determine OS path format, then title the main window accordingly."""
        try:
            if os.name == 'nt':
                project = self.project.split('\\')
            elif os.name == 'posix':
                project = self.project.split('/')
            title = project[-2] + " - " + project[-1]
        except IndexError:
            title = os.getcwd()
        self.winfo_toplevel().title(title)
        print(f"Set main window title to {title}")

    def close_app(self) -> None:
        """Check if a test is running, then close the application."""
        if hasattr(self, 'test'):
            if self.test.running:
                print("Can't close the application while a test is running")
                return
        print("Destroying root")
        self.core.root.destroy()
