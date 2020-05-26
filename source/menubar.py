"""Menu bar for the MainWindow."""

import tkinter as tk  # GUI
from tkinter import filedialog
import os  # handling file paths

from reporter import Reporter
from configmanager import ConfigManager
from concentrations import ConcCalc


class MenuBar(tk.Frame):
    """Menu bar for the main window."""

    def __init__(self, parent, *args, **kwargs):
        """Init the MenuBar."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainwin = parent
        self.core = parent.core
        self.config = self.mainwin.core.config
        plotstyle_list = self.config.get('plot settings', 'plot styles').split(',')
        self.plotstyle_list = [i.strip() for i in plotstyle_list]
        self.build()

    def build(self):
        """Make the Tkinter widgets for the menu bar."""
        self.menubar = tk.Menu(self)
        # self.filemenu = tk.Menu(self, tearoff=0)
        self.menubar.add_command(
            label="Set project folder",
            command=lambda: self.askdir()
        )

        self.menubar.add_command(
            label="Calculate treating volume",
            command=lambda: ConcCalc(self.core)
        )

        self.menubar.add_command(
            label="Make new report",
            command=lambda: Reporter(self.core)
        )

        self.pltstylmenu = tk.Menu(master=self, tearoff=1)
        for style in self.plotstyle_list:
            self.pltstylmenu.add_command(
                label=style,
                command=lambda s=style: self.set_plotstyle(s)
            )
        # check the config to see if we want to show this label to the user
        if self.config.getboolean('plot settings', 'show style options'):
            self.menubar.add_cascade(
                label="Set plot style",
                menu=self.pltstylmenu
            )

        self.menubar.add_command(
            label='Settings',
            command=lambda: self.manageconfig()
        )

        self.menubar.add_command(
            label='Help',
            command=lambda: self.show_help()
        )

        self.mainwin.winfo_toplevel().config(menu=self.menubar)

    def askdir(self):
        """Creates a prompt to ask user for a project folder
        Then sets that as the window title.
        The project variable is a string used to make output file paths later

         """

        out = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select data output directory:"
        )

        if out != "":
            self.mainwin.project = os.path.normpath(out)
            self.config['test settings']['project folder'] = self.mainwin.project
            with open('scalewiz.ini', 'w') as configfile:
                self.config.write(configfile)
                print("Updated 'project folder' in config file")
                print(f"Set project directory to\n{self.mainwin.project}")
            # make it the MainWindow title in a pretty way
            try:
                p = self.mainwin.project.split('\\')
                self.mainwin.title = p[-2] + " - " + p[-1]
                self.mainwin.winfo_toplevel().title(self.mainwin.title)
            except IndexError:
                self.mainwin.winfo_toplevel().title(self.mainwin.project)

    def manageconfig(self):
        """Re-reads the config, then opens a ConfigManager Toplevel"""

        print("Opening ConfigManager")
        self.config.read(self.config.path)
        ConfigManager(
            self.core,
            configpath=self.config.path,
            _title='Settings',
            defaultdict=self.config.DEFAULT_DICT
        )

    def set_plotstyle(self, style: str) -> None:
        """Sets the plot style for MainWindow"""

        print(f"Changing MainWindow plot style to {style}")
        self.mainwin.plotstyle = style
        self.mainwin.pltfrm.configure(text=(f"Style: {self.mainwin.plotstyle}"))

    def show_help(self):
        tk.messagebox.showinfo(
            parent=self,
            title="Help: Using ScaleWiz",
            message=f"""
When you start the program, the pumps should connect automatically.
Clicking the 'COM Ports' label will attempt to reconnect to the pumps.

Set project folder: Sets the folder to put data files in.

Make new report: Opens a new Report Generator window.

Set plot style: Changes the plot style for the plot in the main window (only visible if 'Show Style Options' in settings is set to True)

Settings: Opens a menu to modify the current settings file ('scalewiz.ini') in the directory the program runs out of

Version: {self.core.VERSION}
Website: https://github.com/teauxfu/pct-scalewiz
"""
        )
