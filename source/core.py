"""This is the entry point for the program.
  - imports then creates an instance of MainWindow
  - has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

import serial  # talking to the pumps
import sys  # to sys.exit() on window close
import tkinter as tk  # GUI

from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = MainWindow(self)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    # root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    # root.pack(side="top", fill="both", expand=False)
    root.mainloop()
