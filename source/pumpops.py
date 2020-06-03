"""Module for controlling the pumps directly."""

import os
from time import sleep
import tkinter as tk
from tkinter import ttk
from tkinter import font  # type: ignore
from tkinter.scrolledtext import ScrolledText
import serial
import serial.tools.list_ports
from serial import SerialException
import webbrowser


COMMANDS = ['run', 'stop', 'info', 'pressure', ' ']


class PumpManager(tk.Toplevel):
    """Toplevel for managing settings in an .ini file."""

    def __init__(self, parent):
        """Init with another Tk as parent."""
        tk.Toplevel.__init__(self, parent)
        self.title("Pump Controller")
        if os.name == 'nt':
            self.iconbitmap('chem.ico')
        self.build()

    def build(self):
        """Build all the Tkinter widgets."""
        underline_font = font.Font(font=font.nametofont("TkDefaultFont"))
        underline_font.config(underline=1)
        container = tk.Frame(self)
        device_lbl = tk.Label(container, text="Device:", anchor='w')
        devices = [i.device for i in serial.tools.list_ports.comports()]
        self.device_box = ttk.Combobox(
            container,
            values=devices,
            state='readonly',
            width=10,
            justify='center'
        )
        cmd_lbl = tk.Label(
            container,
            text="Command:",
            anchor='w',
            fg='#0000EE',
            font=underline_font
        )
        self.cmd_box = ttk.Combobox(
            container,
            values=COMMANDS,
            width=10,
            justify='center'
        )
        snd_btn = ttk.Button(
            container,
            text="Send to device",
            command=lambda: self.send_cmd(
                self.device_box.get(),
                self.cmd_box.get()
            )
        )
        out_frm = tk.LabelFrame(container, text="Device responses:")
        self.out_txt = ScrolledText(
            out_frm,
            wrap='word',
            width=30,
            height=9,
            state='disabled'
        )

        device_lbl.grid(row=0, column=0, sticky='e')
        self.device_box.grid(row=0, column=1, sticky='w', pady=2, padx=2)
        cmd_lbl.grid(row=1, column=0, sticky='e')
        self.cmd_box.grid(row=1, column=1, sticky='w', pady=2, padx=2)
        snd_btn.grid(row=2, column=0, columnspan=2)
        self.out_txt.pack()
        out_frm.grid(row=3, column=0, columnspan=2, sticky='ew', padx=2, pady=2)
        self.container.pack(padx=2, pady=2)

        cmd_lbl.bind('<Button-1>', lambda e: webbrowser.open_new(r'https://ssihplc.com/manuals/#next-generation-operators-manuals'))
        self.device_box.bind('<FocusIn>', lambda _: self.container.focus_set())
        self.device_box.bind('<Button-1>', lambda _: self.update_device_box())

    def send_cmd(self, device: str, cmd: str):
        """Try to open a serial port at device, then send an encoded message."""
        if cmd == "run":
            cmd = 'ru'
        if cmd == "stop":
            cmd = 'st'
        if cmd == "info":
            cmd = 'cc'
        if cmd == "pressure":
            cmd = 'pr'

        try:
            cmd = cmd.strip()
            pump = serial.Serial(device, timeout=0.05)
            pump.write(f"{cmd}".encode())
            sleep(0.5)
            self.to_log(pump.readline().decode())
            pump.close()
        except SerialException as error:
            self.to_log("Cannot stop the pump while a test is running.")
            print(error)
        except FileNotFoundError as error:
            print(error)
            self.to_log(error)

    def to_log(self, *msgs) -> None:
        """Log a message to the Text widget in MainWindow's outfrm."""
        for msg in msgs:
            self.out_txt['state'] = 'normal'
            self.out_txt.insert('end', f"{msg}" + "\n")
            self.out_txt['state'] = 'disabled'
            self.out_txt.see('end')

    def update_device_box(self):
        """Updates the device_box attribute with a current device list."""
        devices = [i.device for i in serial.tools.list_ports.comports()]
        self.device_box.configure(values=devices)
