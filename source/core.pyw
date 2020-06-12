"""This is the entry point for the program.

- imports then creates an instance of MainWindow
- has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

from configparser import ConfigParser
import os
from concurrent.futures import ThreadPoolExecutor  # handling the test
import tkinter as tk  # GUI
from tkinter import font  # type: ignore
import settings
from mainwindow import MainWindow
from iconer import set_window_icon


class ScaleWiz(tk.Frame):
    """Core class for the application."""

    VERSION = '[0.7.4]'

    def __init__(self, parent):
        """Instantiate the core."""
        tk.Frame.__init__(self, parent)
        self.root = parent
        self.parser = ConfigParser()
        self.parser.DEFAULT_DICT = settings.DEFAULT_DICT
        if not os.path.isfile('assets/scalewiz.ini'):
            settings.make_config(self.parser)
        self.parser.path = os.path.abspath('assets/scalewiz.ini')
        self.parser.read(self.parser.path)
        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=2)


if __name__ == "__main__":
    root = tk.Tk()
    set_window_icon(root)
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Arial")
    root.option_add("*Font", "TkDefaultFont")
    root.tk_setPalette(background='#F0F0F0')
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
