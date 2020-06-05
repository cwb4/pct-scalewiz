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


def set_window_icon(window):
    """Check what OS we're on, and set the window icon if on Windows."""
    try:
        if os.name == 'nt':
            window.iconbitmap('assets/chem.ico')
    except FileNotFoundError:
        print("The icon file at assets/chem.ico could not be found.")
    except Exception as error:
        print(error)


class ScaleWiz(tk.Frame):
    """Core class for the application."""

    VERSION = '[0.7.3]'

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
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)


if __name__ == "__main__":
    root = tk.Tk()
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Arial")
    root.option_add("*Font", "TkDefaultFont")
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    set_window_icon(root)
    root.mainloop()
