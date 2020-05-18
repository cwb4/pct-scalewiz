"""A class to handle the logic for running the test"""

import csv  # logging the data
from datetime import datetime  # logging the data
import os  # handling file paths
import serial
from serial import SerialException
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

        print("Disabling MainWindow test parameter entries")
        for child in self.mainwin.entfrm.winfo_children():
            child.configure(state="disabled")

        print("Enabling MainWindow test controls")
        for child in self.mainwin.cmdfrm.winfo_children():
            child.configure(state="normal")

        # clear the text widget
        self.mainwin.dataout['state'] = 'normal'
        self.mainwin.dataout.delete(1.0, 'end')
        self.mainwin.dataout['state'] = 'disabled'

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
        except SerialException:
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

    def run_test(self) -> None:
        """Submits a test loop to the thread_pool_executor"""

        if not self.running:
            self.to_log("Starting the test")
            self.core.thread_pool_executor.submit(self.take_reading)
            self.running = True
            self.core.root.protocol("WM_DELETE_WINDOW", lambda: self.close_app())

    def take_reading(self) -> None:
        """Loop to be handled by the thread_pool_executor"""

        for pump in (self.pump1, self.pump2):
            pump.write('ru'.encode())
        # let the pumps warm up before we start recording data
        time.sleep(3)

        # a dict to hold recent pressure readings
        pressures = {
                    'PSI 1' : [1, 1, 1, 1, 1],
                    'PSI 2' : [1, 1, 1, 1, 1]
                    }
        psi1, psi2, self.elapsed = 0, 0, 0
        self.interval = self.core.config.getint(
            'test settings', 'interval seconds'
        )
        starttime = time.time()
        self.readings = 0
        reading_start = time.time()
        while (
         (psi1 < self.failpsi or psi2 < self.failpsi)
        and (
             self.elapsed <= self.timelimit*60
             or self.readings <= self.timelimit*60/self.interval
             )
        and self.running
         ):

            if time.time() - reading_start >= self.interval:
                if self.readings != 0 and self.elapsed/self.readings - self.interval > 0.01:
                    print(f"avg s/reading: {round(self.elapsed/self.readings, 4)}")

                reading_start = time.time()
                try:
                    for pump in (self.pump1, self.pump2):
                        pump.write('cc'.encode())  # get current conditions
                    time.sleep(0.05)  # give a moment to respond
                    psi1 = int(self.pump1.readline().decode().split(',')[1])
                    psi2 = int(self.pump2.readline().decode().split(',')[1])
                except SerialException as e:
                    self.to_log(e)

                thisdata = [
                            time.strftime("%I:%M:%S", time.localtime()),
                            round(self.elapsed),  # as seconds
                            f"{self.elapsed/60:.2f}",  # as minutes
                            psi1,
                            psi2
                            ]
                with open(self.outpath, "a", newline='') as f:
                    csv.writer(f, delimiter=',').writerow(thisdata)
                this_reading = (
                    f"{self.elapsed/60:.2f} min, {psi1} psi, {psi2} psi"
                )
                self.to_log(this_reading)
                self.readings += 1
                self.elapsed = time.time() - starttime
                # end of while loop

        print("Test complete")
        self.end_test()
        for i in range(3):
            print('\a')
            time.sleep(0.5)

    def end_test(self) -> None:
        """Stops the pumps and closes their COM ports, then swaps the button
        states for the entfrm and cmdfrm widgets"""

        print("Ending the test")
        if self.running:
            try:
                for pump in (self.pump1, self.pump2):
                    pump.write('st'.encode())
                    pump.close()
            except SerialException as e:
                print("Failed to send stop/close order to pump")
                print(e)

        max_measures = round(self.elapsed/self.interval)  # for this particular run
        self.to_log(f"Took {self.readings}/{max_measures} expected readings in {self.elapsed/60:.2f} min")
        completion_rate = round(self.readings/max_measures*100)
        self.to_log(f"Dataset is {completion_rate}% complete")

        self.running = False
        # re-enable the entries to let user start new test
        for child in self.mainwin.entfrm.winfo_children():
            child.configure(state="normal")
        # disable the run/end buttons until a new test is started
        for child in self.mainwin.cmdfrm.winfo_children():
            child.configure(state="disabled")

    def close_app(self):

        if self.running:
            print("Can't close the application while a test is running")
        else:
            print("Destroying root")
            self.core.root.destroy()
