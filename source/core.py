"""This is the entry point for the program.
  - imports then creates an instance of MainWindow
  - has a thread_pool_executor attribute for a blocking loop made in MainWindow
"""

from concurrent.futures import ThreadPoolExecutor  # handling the test loop
import serial  # talking to the pumps
import sys  # to sys.exit() on window close
import tkinter as tk  # GUI

from mainwindow import MainWindow


class ScaleWiz(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = MainWindow(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

def close_ports():  # attempts to close all open ports, just in case
    """Tries to close any open COM ports."""
    ports = ["COM" + str(i) for i in range(15)]
    for i in ports:
        try:
            if serial.Serial(i).is_open:
                print(f"Closing {i}")
                serial.Serial(i).close
        except serial.SerialException:
            pass
    print("Destroying root")
    root.destroy()
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0, 0)
    ScaleWiz(root).pack(side="top", fill="both", expand=False)
    root.protocol("WM_DELETE_WINDOW", close_ports)
    root.mainloop()
