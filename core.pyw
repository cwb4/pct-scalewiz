"""The core ScaleWiz module.


Todo:
    * tie in the menubar
    * rebuild the plotter util

"""
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

from mainwindow import MainWindow
from menubar import MenuBar

class ScaleWiz(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = MainWindow(self)
        self.menu = MenuBar(self)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0,0)
    thread_pool_executor = ThreadPoolExecutor(max_workers=1)
    ScaleWiz(root).pack(side="top", fill="both", expand=False)
    root.mainloop()
