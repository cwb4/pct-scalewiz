"""This is the entry point for the program.
  - imports then creates an instance of MainWindow
  - has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

import configparser
import os
from concurrent.futures import ThreadPoolExecutor  # handling the test loop
import serial  # talking to the pumps
import sys  # to sys.exit() on window close
import tkinter as tk  # GUI

from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    """Docstring"""
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.config = configparser.ConfigParser()
        if not os.path.exists('config.ini'):
            print("Making new config.ini")
            self.config['plot settings'] = {
            'default style' : 'bmh',
            'show style options' : 'True',
            'plot styles' : """
                bmh,
                fivethirtyeight,
                seaborn,
                seaborn-colorblind,
                seaborn-dark-palette,
                seaborn-muted,
                seaborn-notebook,
                seaborn-paper,
                seaborn-pastel,
                tableau-colorblind10
                """,
            'color cycle' : """
                orange,
                blue,
                red,
                mediumseagreen,
                darkgoldenrod,
                indigo,
                mediumvioletred,
                darkcyan,
                maroon,
                darkslategrey
                """,
            }
            self.config['report settings'] = {
            'date format' : '',
            'template path' : '',
            'max series' : 10,
            }

            self.config['test settings'] = {
            'fail psi' : 1500,
            'time limit minutes' : 90,
            'default pump' : 'PSI 2',
            'last proj dir' : '',
            }
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
        else:
            print("Found config.ini")
        self.config.read('config.ini')

        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)


def close_app():  # attempts to close all open ports, just in case
    # rlly should be no need for this ...
    list = serial.tools.list_ports.comports()
    ports = [i.device for i in list]
    for i in ports:
            if serial.Serial(i).is_open:
                serial.Serial(i).write('st'.encode())
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
    root.protocol("WM_DELETE_WINDOW", close_app)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    # root.pack(side="top", fill="both", expand=False)
    root.mainloop()
