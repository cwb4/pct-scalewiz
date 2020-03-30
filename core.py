"""The core ScaleWiz module.


Todo:
    *

"""
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from mainwindow import MainWindow
from menubar import MenuBar

class ScaleWiz(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = MainWindow(self)
        self.menu = MenuBar(self)
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scale Block Wizard")
    root.resizable(0,0)
    ScaleWiz(root).pack(side="top", fill="both", expand=False)

    def close_ports(): # attempts to close all open ports, just in case
        import serial
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
        exit()
    root.protocol("WM_DELETE_WINDOW", close_ports)
    root.mainloop()
