"""A class to handle the logic for running the test"""

import csv  # logging the data
from datetime import datetime  # logging the data

import os  # handling file paths
import serial
import tkinter as tk  # GUI
import time  # sleeping
from winsound import Beep  # beeping when the test ends


class Experiment(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """Collects all the user data from the MainWindow widgets"""

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.core = parent.core

        print("Disabling MainWindow parameter entries")
        for child in self.parent.entfrm.winfo_children():
            child.configure(state="disabled")

        print("Enabling MainWindow test controls")
        for child in self.parent.cmdfrm.winfo_children():
            child.configure(state="normal")

        # clear the text widget
        self.parent.dataout['state'] = 'normal'
        self.parent.dataout.delete(1.0, 'end')
        self.parent.dataout['state'] = 'disabled'
        # get user input from the main window
        self.port1 = self.parent.port1.get()
        self.port2 = self.parent.port2.get()
        self.timelimit = float(self.parent.timelim.get())
        self.failpsi = int(self.parent.failpsi.get())
        self.chem = self.parent.chem.get().strip().replace(' ', '_')
        self.conc = self.parent.conc.get().strip().replace(' ', '_')
        # set up an output file
        file_name = f"{self.chem}_{self.conc}.csv"
        self.outpath = os.path.join(self.parent.project, file_name)
        # make sure we don't overwrite existing data
        while os.path.isfile(self.outpath):  # we haven't made one yet
            self.to_log("A file with that name already exists",
                        "Making a copy instead")
            self.outpath = self.outpath[0:-4]
            self.outpath += r" - copy.csv"
        self.to_log(f"Creating output file at \n{self.outpath}")
        header_row = ["Timestamp", "Seconds", "Minutes", "PSI 1", "PSI 2"]
        with open(self.outpath, "w") as f:
            csv.writer(f, delimiter=',').writerow(header_row)

        self.psi1, self.psi2, self.elapsed = 0, 0, 0

        # the timeout values are an alternative to using TextIOWrapper
        try:
            self.pump1 = serial.Serial(self.port1, timeout=0.05)
            self.pump2 = serial.Serial(self.port2, timeout=0.05)
        except serial.serialutil.SerialException:
            self.to_log("Could not establish a connection to the pumps",
                        "Try resetting the port connections")
            print("Disabling MainWindow test controls")
            for child in self.parent.cmdfrm.winfo_children():
                child.configure(state="disabled")
            print("Enabling MainWindow parameter entries")
            for child in self.parent.entfrm.winfo_children():
                child.configure(state="normal")

    def to_log(self, *msgs) -> None:
        """Passes str messages to the parent widget's to_log method"""

        self.parent.to_log(*msgs)

    def end_test(self) -> None:
        """Stops the pumps and closes their COM ports, then swaps the button
        states for the entfrm and cmdfrm widgets"""

        print("Ending the test")
        for pump in (self.pump1, self.pump2):
            pump.write('st'.encode())
            pump.close()
        self.to_log(f"The test finished in {self.elapsed/60:.2f} minutes")

        # TODO: try just disabling the frames instead, half the lines
        # re-enable the entries to let user start new test
        for child in self.parent.entfrm.winfo_children():
            child.configure(state="normal")
        # disable the run/end buttons until a new test is started
        for child in self.parent.cmdfrm.winfo_children():
            child.configure(state="disabled")

    def run_test(self) -> None:
        """Submits a test loop to the thread_pool_executor"""

        self.to_log("Starting the test")
        self.core.thread_pool_executor.submit(self.take_reading)

    def take_reading(self) -> None:
        """Loop to be handled by the thread_pool_executor"""

        for pump in (self.pump1, self.pump2):
            pump.write('ru'.encode())
        # let the pumps warm up before we start recording data
        time.sleep(3)

        starttime = datetime.now()

        # a dict to hold recent pressure readings
        pressures = {'PSI 1' : [1, 1, 1, 1, 1],
                     'PSI 2' : [1, 1, 1, 1, 1]
                    }

        while (
         (self.psi1 < self.failpsi or self.psi2 < self.failpsi)
         and self.elapsed < self.timelimit*60
         ):
            reading_start = time.time()
            self.elapsed = (datetime.now() - starttime).seconds
            for pump in (self.pump1, self.pump2):
                pump.write('cc'.encode())  # get current conditions
            time.sleep(0.1)
            self.psi1 = int(self.pump1.readline().decode().split(',')[1])
            self.psi2 = int(self.pump2.readline().decode().split(',')[1])
            thisdata = [
                        time.strftime("%I:%M:%S", time.localtime()),
                        self.elapsed,  # as seconds
                        f'{self.elapsed/60:.2f}',  # as minutes
                        self.psi1,
                        self.psi2
                        ]
            with open(self.outpath, "a", newline='') as f:
                csv.writer(f, delimiter=',').writerow(thisdata)

            nums = (self.elapsed/60, self.psi1, self.psi2)
            this_reading = (
                f"{self.elapsed/60:.2f} min, {self.psi1} psi, {self.psi2} psi"
            )
            self.to_log(this_reading)

            # make sure we have flow - consecutive 0 readings alert user
            pressures['PSI 1'].insert(0, self.psi1)
            pressures['PSI 1'].pop(-1)
            pressures['PSI 2'].insert(0, self.psi2)
            pressures['PSI 2'].pop(-1)
            for list in (pressures['PSI 1'], pressures['PSI 2']):
                if list.count(0) is 3: Beep(750, 500)
<<<<<<< HEAD

            time.sleep(1 - (time.time() - reading_start))  # 1 reading/s
=======
            try:
                time.sleep(1 - (time.time() - start))
            except ValueError as e:  # sleep doesn't take args < 0
                print(e)
>>>>>>> fd0f417e09a283e302010fb4c1e2d3bea53485ac
            # end of while loop

        print("Test complete; ending test")
        self.end_test()
        for i in range(3):
            Beep(750, 500)
            time.sleep(0.5)
