"""This is the entry point for the program.
  - imports then creates an instance of MainWindow
  - has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

import configparser
from concurrent.futures import ThreadPoolExecutor  # handling the test loop
import serial  # talking to the pumps
import sys  # to sys.exit() on window close
import tkinter as tk  # GUI

from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    # list of matplotlib styles
    PLOT_STYLES = [
        "bmh",
        "fivethirtyeight",
        "seaborn",
        "seaborn-colorblind",
        "seaborn-dark-palette",
        "seaborn-muted",
        "seaborn-notebook",
        "seaborn-paper",
        "seaborn-pastel",
        "tableau-colorblind10"
        ]
    # color cycle to use when plotting multiple series
    COLOR_CYCLE = [
        'orange', 'blue', 'red',
        'mediumseagreen', 'darkgoldenrod', 'indigo', 'mediumvioletred',
        'darkcyan', 'maroon', 'darkslategrey'
         ]



    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)
        self.config = configparser.ConfigParser()
        config.read('config.ini')

def close_ports():  # attempts to close all open ports, just in case
    list = serial.tools.list_ports.comports()
    ports = [i.device for i in list]
    for i in ports:
            if serial.Serial(i).is_open:
                print(f"Closing {i}")
                serial.Serial(i).close
                # serial exception here if test running -
                # call to end_test also?
    print("Destroying root")
    root.destroy()
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    root.protocol("WM_DELETE_WINDOW", close_ports)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    # root.pack(side="top", fill="both", expand=False)
    root.mainloop()
