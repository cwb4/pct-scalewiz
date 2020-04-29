"""The MenuBar for the MainWindow"""

import tkinter as tk  # GUI
from tkinter import filedialog
import os  # handling file paths

from reporter import Reporter
from config import ConfigManager


class MenuBar(tk.Frame):
    """Docstring"""
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainwin = parent
        self.core = parent.core
        self.config = self.mainwin.core.config
        self.plotstyle_list = self.config.get(
            'plot settings', 'plot styles'
            ).split(',')
        self.build()

    def build(self):
        self.menubar = tk.Menu(self)
        # self.filemenu = tk.Menu(self, tearoff=0)
        self.menubar.add_command(
            label="Set project folder",
            command=self.askdir
            )

        self.pltmenu = tk.Menu(master=self, tearoff=0)
        self.pltmenu.add_command(
            label="Make new report",
            command=self.new_plot
        )

        self.pltstylmenu = tk.Menu(master=self, tearoff=1)
        for style in self.plotstyle_list:
            self.pltstylmenu.add_command(
                label=style,
                command=lambda s = style: self.set_plotstyle(s)
            )
        # check the config to see if we want to show this label to the user
        if self.config.getboolean('plot settings', 'show style options'):
            self.pltmenu.add_cascade(
                label="Set plot style",
                menu=self.pltstylmenu
            )

        self.menubar.add_cascade(
            label="Report",
            menu=self.pltmenu
        )

        self.menubar.add_command(
            label='Settings',
            command=self.manageconfig
        )

        self.mainwin.winfo_toplevel().config(menu=self.menubar)

    def askdir(self):
        """Creates a prompt to ask user for a project folder,
         then sets that as the window title.
         The project variable is a string used to make output file paths later
         """

        out = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select data output directory:"
            )

        if out is not "":
            self.mainwin.project = os.path(out)
            self.config['test settings']['project folder'] = self.mainwin.project
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
                print("Updated 'project folder' in config file")
            # make it the MainWindow title in a pretty way
            p = out.split('\\')
            pp = p[-2] + " - " + p[-1]
            self.mainwin.winfo_toplevel().title(pp)
            print(f"Set project directory to\n{self.mainwin.project}")

    def manageconfig(self):
        ConfigManager(self)

    def set_plotstyle(self, style: str) -> None:
        """Sets the plot style for MainWindow"""

        print(f"Changing MainWindow plot style to {style}")
        self.mainwin.plotstyle = style
        self.mainwin.pltfrm.configure(text=(f"Style: {self.plotstyle}"))

    def new_plot(self):
        """Spawns a new Plotter window"""

        print("Spawning a new Reporter")
        Reporter(self)
