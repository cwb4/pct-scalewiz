"""This is the entry point for the program.

- imports then creates an instance of MainWindow
- has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

from configparser import ConfigParser
import os
from concurrent.futures import ThreadPoolExecutor  # handling the test
import tkinter as tk  # GUI
import settings
from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    """Core class for the application."""

    VERSION = '[0.7.1]'

    def __init__(self, parent):
        """Instantiate the core."""
        tk.Frame.__init__(self, parent)
        self.root = parent
        self.parser = ConfigParser()
        self.parser.DEFAULT_DICT = settings.DEFAULT_DICT
        if not os.path.isfile('scalewiz.ini'):
            settings.make_config(self.parser)
        self.parser.path = os.path.abspath('scalewiz.ini')

        self.parser.read(self.parser.path)
        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    if os.name == 'nt':
        root.iconbitmap('chem.ico')
    root.mainloop()
