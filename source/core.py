"""This is the entry point for the program.

- imports then creates an instance of MainWindow
- has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

import configparser
import os
from concurrent.futures import ThreadPoolExecutor  # handling the test
import tkinter as tk  # GUI
import settings

from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    """Core class for the application."""

    VERSION = '[0.6.3x]'


    def __init__(self, parent):
        """Instantiate the core."""
        tk.Frame.__init__(self, parent)
        self.root = parent
        self.config = configparser.ConfigParser()
        # self.config.DEFAULT_DICT = ScaleWiz.DEFAULT_DICT
        self.config.DEFAULT_DICT = settings.DEFAULT_DICT

        if not os.path.isfile('scalewiz.ini'):
            self.make_config()
        else:
            print("Found scalewiz.ini")
            self.config.path = os.path.abspath('scalewiz.ini')

        self.config.read(self.config.path)
        default_sections = [i for i in self.config.DEFAULT_DICT]
        if self.config.sections() != default_sections:
            print("The found config didn't have the right sections")
            self.make_config()

        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

    def make_config(self):
        """Create a default scalewiz.ini in the current working directory."""
        print("Making new scalewiz.ini file in \n" + f"{os.getcwd()}")
        self.config.read_dict(self.config.DEFAULT_DICT)
        with open('scalewiz.ini', 'w') as configfile:
            self.config.write(configfile)
            self.config.path = os.path.abspath('scalewiz.ini')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    if os.name == 'nt':
        root.iconbitmap('chem.ico')
    root.mainloop()
