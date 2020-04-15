"""A class to handle the logic for running the test"""

import csv  # logging the data
from datetime import datetime  # logging the data
from concurrent.futures import ThreadPoolExecutor  # handling the test loop
import os  # handling file paths
import tkinter as tk  # GUI
import time  # sleeping
from winsound import Beep  # beeping when the test ends


class Experiment(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """Collects all the user data from the MainWindow widgets"""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.port1 = self.parent.port1.get()
        self.port2 = self.parent.port2.get()
        self.timelimit = double(self.parent.timelim.get())
        self.failpsi = self.parent.failpsi.get()
        self.chem = self.parent.chem.get()
        self.conc = self.parent.conc.get()

        self.outfile = f"{self.chem}_{self.conc}.csv"
        self.savepath = self.parent.project
        self.outpath = os.path.join(self.savepath, self.outfile)

        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)
        self.psi1, self.psi2, self.elapsed = 0, 0, 0

        # the timeout values are an alternative to using TextIOWrapper
        self.pump1 = serial.Serial(self.port1, timeout=0.01)
        self.pump2 = serial.Serial(self.port2, timeout=0.01)

    def to_log(self, msg) -> None:
        """Logs a message to the Text widget in MainWindow's outfrm"""
        self.parent.to_log(msg)

    def end_test(self) -> None:
        """Stops the pumps and closes their COM ports, then swaps the button
        states for the entfrm and cmdfrm widgets"""

        for pump in (self.pump1, self.pump2):
            pump.write('st'.encode())
            pump.close()

        msg = "The test finished in {0:.2f} minutes".format(self.elapsed/60)
        self.to_log(msg)

        # re-enable the entries to let user start new test
        for child in self.parent.entfrm.winfo_children():
            child.configure(state="normal")
        # disable the run/end buttons until a new test is started
        for child in self.parent.cmdfrm.winfo_children():
            child.configure(state="disabled")

    def run_test(self) -> None:
        """Submits a test loop to the thread_pool_executor"""

        self.to_log(f"Creating output file at \n{self.outpath}")
        header_row = ["Timestamp", "Seconds", "Minutes", "PSI 1", "PSI 2"]
        with open(self.outpath, "w") as f:
            csv.writer(f, delimiter=',').writerow(header_row)

        # disable the entries for test parameters
        for child in self.parent.entfrm.winfo_children():
            child.configure(state="disabled")

        # enable the commands for starting/stopping the test
        for child in self.parent.cmdfrm.winfo_children():
            child.configure(state="normal")

        self.to_log("Starting the test...")
        for pump in (self.pump1, self.pump2):
            pump.write('ru'.encode())
        # let the pumps warm up before we start recording data
        time.sleep(3)
        self.thread_pool_executor.submit(self.take_reading)

    def take_reading(self) -> None:
        """Loop to be handled by the thread_pool_executor"""

        starttime = datetime.now()
        while (
         (self.psi1 < self.failpsi or self.psi2 < self.failpsi)
         and self.elapsed < self.timelimit*60
         ):
            for pump in (self.pump1, self.pump2):
                pump.write('cc'.encode())

            time.sleep(0.1)

            self.psi1 = int(self.pump1.readline().decode().split(',')[1])
            self.psi2 = int(self.pump2.readline().decode().split(',')[1])

            thisdata = [
                        time.strftime("%I:%M:%S", time.localtime()),
                        self.elapsed,  # as seconds
                        # TODO: learn how to do this with a real f-string
                        '{0:.2f}'.format(self.elapsed/60),  # as minutes
                        self.psi1,
                        self.psi2
                        ]
            with open(self.outpath, "a", newline='') as f:
                csv.writer(f, delimiter=',').writerow(thisdata)

            nums = ((self.elapsed/60), self.psi1, self.psi2)
            this_reading = ("{0:.2f} min, {1} psi, {2} psi".format(nums))
            self.to_log(this_reading)

            time.sleep(0.9)
            self.elapsed = (datetime.now() - starttime).seconds
            # end of while loop

        self.end_test()

        for i in range(3):
            Beep(750, 500)
            time.sleep(0.5)