"""Menu bar for the MainWindow."""

import tkinter as tk  # GUI
from tkinter import filedialog
import os  # handling file paths

from reporter import Reporter
from concentrations import ConcCalc
from settings import ConfigManager


class MenuBar(tk.Frame):
    """Menu bar for the main window."""

    def __init__(self, parent, *args, **kwargs):
        """Init the MenuBar."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainwin = parent
        self.core = parent.core
        self.parser = self.mainwin.core.parser
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

        self.menubar.add_command(
            label='Settings',
            command=lambda: self.manage_config()
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
            self.parser['test settings']['project folder'] = self.mainwin.project
            with open('scalewiz.ini', 'w') as configfile:
                self.parser.write(configfile)
            print("Updated 'project folder' in config file")
            print(f"Set project directory to\n{self.mainwin.project}")
            self.mainwin.update_title()

    def manage_config(self):
        """Re-reads the config, then opens a ConfigManager Toplevel"""
        print("Opening ConfigManager")
        self.parser.read(self.parser.path)
        ConfigManager(self.core, self.parser)
        self.parser.read(self.parser.path)

    def show_help(self):
        """Show a help dialog."""
        tk.messagebox.showinfo(
            parent=self,
            title="Help: Using ScaleWiz",
            message=f"""
Set project folder: Sets the folder to put data files in.

Make new report: Opens a new Report Generator window.

Settings: Opens a menu to modify the current settings file ('scalewiz.ini') in the directory the program runs out of.

Version: {self.core.VERSION}
Website: https://github.com/teauxfu/pct-scalewiz
"""
        )
