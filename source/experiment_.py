"""A class to handle the logic for running the test"""

import csv  # logging the data
from concurrent.futures import ThreadPoolExecutor  # handling the test loop
from datetime import datetime  # logging the data
import os  # handling file paths
import serial
# import tkinter as tk  # GUI
import time  # sleeping


class Experiment():
    def __init__(self, parent, port1, port2, timelimit, failpsi, chem, conc):
        """Collects all the user data from the MainWindow widgets"""

        self.mainwin = parent
        self.core = self.mainwin.core
        self.port1 = port1
        self.port2 = port2
        self.timelimit = timelimit
        self.failpsi = failpsi
        self.chem = chem
        self.conc = conc
        self.running = False

        print("Disabling MainWindow parameter entries")
        for child in self.mainwin.entfrm.winfo_children():
            child.configure(state="disabled")

        print("Enabling MainWindow test controls")
        for child in self.mainwin.cmdfrm.winfo_children():
            child.configure(state="normal")

        # clear the text widget
        self.mainwin.dataout['state'] = 'normal'
        self.mainwin.dataout.delete(1.0, 'end')
        self.mainwin.dataout['state'] = 'disabled'
        # get user input from the main window

        # set up an output file
        file_name = f"{self.chem}_{self.conc}.csv"
        self.outpath = os.path.join(self.mainwin.project, file_name)
        # make sure we don't overwrite existing data
        while os.path.isfile(self.outpath):  # we haven't made one yet
            self.to_log("A file with that name already exists",
                        "Making a copy instead")
            self.outpath = self.outpath[0:-4]
            self.outpath += r" - copy.csv"
        self.to_log(f"Creating output file at \n{self.outpath}")
        print(f"Creating output file at \n{self.outpath}")

        header_row = ["Timestamp", "Seconds", "Minutes", "PSI 1", "PSI 2"]
        with open(self.outpath, "w") as f:
            csv.writer(f, delimiter=',').writerow(header_row)

        # the timeout values are an alternative to using TextIOWrapper
        # the values chosen were suggested by the pump's documentation
        try:
            self.pump1 = serial.Serial(self.port1, timeout=0.05)
            self.pump2 = serial.Serial(self.port2, timeout=0.05)
        except serial.serialutil.SerialException:
            self.to_log("Could not establish a connection to the pumps",
                        "Try resetting the port connections")
            print("Disabling MainWindow test controls")
            for child in self.mainwin.cmdfrm.winfo_children():
                child.configure(state="disabled")
            print("Enabling MainWindow parameter entries")
            for child in self.mainwin.entfrm.winfo_children():
                child.configure(state="normal")

    def to_log(self, *msgs) -> None:
        """Passes str messages to the parent widget's to_log method"""

        self.mainwin.to_log(*msgs)

    def end_test(self) -> None:
        """Stops the pumps and closes their COM ports, then swaps the button
        states for the entfrm and cmdfrm widgets"""

        print("Ending the test")
        for pump in (self.pump1, self.pump2):
            pump.write('st'.encode())
            pump.close()
        self.to_log(f"The test finished in {self.elapsed/60:.2f} minutes")
        self.running = False
        # re-enable the entries to let user start new test
        for child in self.mainwin.entfrm.winfo_children():
            child.configure(state="normal")
        # disable the run/end buttons until a new test is started
        for child in self.mainwin.cmdfrm.winfo_children():
            child.configure(state="disabled")

    def run_test(self) -> None:
        """Submits a test loop to the thread_pool_executor"""
        if not self.running:
            self.to_log("Starting the test")
            self.running = True
            with self.core.thread_pool_executor as executor:
                executor.submit(self.take_reading)
                # for future in concurrent.futures.as_completed(this_test):
                #     print(repr(future.exception()))

    def take_reading(self) -> None:
        """Loop to be handled by the thread_pool_executor"""


        # a dict to hold recent pressure readings
        pressures = {
                    'PSI 1' : [1, 1, 1, 1, 1],
                    'PSI 2' : [1, 1, 1, 1, 1]
                    }
        self.psi1, self.psi1, self.elapsed = 0, 0, 0
        interval = self.core.config.getint(
            'test settings', 'interval seconds'
        )
        self.starttime = time.time()
        last_reading = time.time()
        self.reads = 0

        for pump in (self.pump1, self.pump2):
            pump.write('ru'.encode())
        # let the pumps warm up before we start recording data
        time.sleep(3)

        while (
         (self.psi1 < self.failpsi or self.psi1 < self.failpsi)
         and self.elapsed < self.timelimit*60
         and self.reads < self.timelimit*60/interval
         ):
            print("checking ...")
            if time.time() - last_reading >= interval:
                print("reading ...")
                last_reading = time.time()
                try:
                    (this_data, this_reading) = self.read()
                    self.to_log(this_reading)
                    with open(self.outpath, "a", newline='') as f:
                        csv.writer(f, delimiter=',').writerow(this_data)
                except Exception as e:
                    raise e
                self.reads += 1
                self.elapsed = time.time() - self.starttime
                print(f"finished reading at {round(self.elapsed)}")

            # if self.reads != 0 and self.elapsed/self.reads - interval > 0.01:
            #     print(f"avg s/reading: {round(self.elapsed/self.reads, 4)}")

        # end of while loop
        print("Test complete")
        self.end_test()
        for i in range(3):
            print('\a')
            time.sleep(0.5)

    def read(self):

        for pump in (self.pump1, self.pump2):
            pump.write('cc'.encode())  # get current conditions
        time.sleep(0.05)  # give a moment to respond
        self.psi1 = int(self.pump1.readline().decode().split(',')[1])
        self.psi1 = int(self.pump2.readline().decode().split(',')[1])
        this_data = [
                    time.strftime("%I:%M:%S", time.localtime()),
                    round(self.elapsed),  # as seconds
                    f"{self.elapsed/60:.2f}",  # as minutes
                    self.psi1,
                    self.psi1
                    ]
        # with open(self.outpath, "a", newline='') as f:
        #     csv.writer(f, delimiter=',').writerow(this_data)

        this_reading = (
            f"{self.elapsed/60:.2f} min, {self.psi1} psi, {self.psi1} psi"
        )
        # self.to_log(this_reading)

        # make sure we have flow - consecutive 0 readings alert user
        pressures['PSI 1'].insert(0, self.psi1)
        pressures['PSI 1'].pop(-1)
        pressures['PSI 2'].insert(0, self.psi1)
        pressures['PSI 2'].pop(-1)
        for list in (pressures['PSI 1'], pressures['PSI 2']):
            if list.count(0) >= 3:
                print(f"{list.count(0)} null values in the past 5 readings")
                print('\a')
        return this_data, this_reading
