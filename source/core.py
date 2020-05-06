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
    """This class """

    VERSION = '[0.5.3]'

    DEFAULT_DICT = {
        'plot settings': {
            'default style': 'bmh',
            'show style options': 'True',
            'plot styles': """bmh, fivethirtyeight, seaborn, seaborn-colorblind, seaborn-dark-palette, seaborn-muted, seaborn-notebook, seaborn-paper, seaborn-pastel, tableau-colorblind10""",
        'color cycle':"""orange, blue, red, mediumseagreen, darkgoldenrod, indigo, mediumvioletred, darkcyan, maroon, darkslategrey"""
        },
        'report settings': {
            'template path': '',
            'series per project': '10'
        },
        'test settings': {
            'fail psi': '1500',
            'default baseline' : 75,
            'time limit minutes': '90',
            'default pump': 'PSI 2',
            'project folder': '',
        }
    }

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.DEFAULT_DICT = ScaleWiz.DEFAULT_DICT
        if not os.path.isfile('scalewiz.ini'):
            self.make_config()
        else:
            print("Found scalewiz.ini")
            self.config.path = os.path.abspath('scalewiz.ini')

        self.config.read('scalewiz.ini')
        default_sections = [i for i in ScaleWiz.DEFAULT_DICT.keys()]
        if not self.config.sections() == default_sections:
            print("The found config didn't have the right sections")
            self.make_config()

        self.mainwin = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

    def make_config(self):
        """Creates a default scalewiz.ini in the current working directory"""

        print("Making new scalewiz.ini file in \n" + f"{os.getcwd()}")
        self.config.read_dict(ScaleWiz.DEFAULT_DICT)
        with open('scalewiz.ini', 'w') as configfile:
            self.config.write(configfile)
            self.config.path = os.path.abspath('scalewiz.ini')

def close_app():  # attempts to close all open ports, just in case
    list = serial.tools.list_ports.comports()
    ports = [i.device for i in list]
    for i in ports:
            if serial.Serial(i).is_open:
                serial.Serial(i).write('st'.encode())
                print(f"Closing {i}")
                try:
                    serial.Serial(i).close
                except SerialException as e:
                    print(e)
                    print("Couldn't close COM port; is a dupe process running?")

    print("Destroying root")
    root.destroy()
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    root.protocol("WM_DELETE_WINDOW", close_app)
    ScaleWiz(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
