"""A Toplevel to manage settings from a ConfigParser object."""

import os
from configparser import ConfigParser
import tkinter as tk
from tkinter import ttk
from tkinter import font  # type: ignore

DEFAULT_DICT = {
    'test settings': {
        'fail psi': '1500',
        'default baseline': 75,
        'time limit minutes': '90',
        'interval seconds': '3',
        'default pump': 'PSI 2',
        'project folder': '',
    },
    'report settings': {
        'template path': '',
        'color cyle': """orange, blue, red, mediumseagreen, darkgoldenrod,
        indigo, mediumvioletred, darkcyan, maroon, darkslategrey"""
    }
}


class ConfigManager(tk.Toplevel):
    """Toplevel for managing settings in an .ini file."""

    def __init__(self, parent, parser: ConfigParser):
        """Init with another Tk as parent."""
        tk.Toplevel.__init__(self, parent)
        self.parser = parser
        self.title('Settings')
        self.build()
        self.fill_form()

    def build(self):
        """Make all the widgets."""
        # setup
        vcmd = (self.register(self.is_numeric))
        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')

        # frame for test settings
        test_frm = tk.LabelFrame(self, text="Test Settings", font=bold_font)

        # the labels
        psi_lbl = ttk.Label(test_frm, text="Failure threshold (psi):", anchor='w')
        time_lbl = ttk.Label(test_frm, text="Time limit (min):", anchor='w')
        int_lbl = ttk.Label(test_frm, text="Reading interval (s per reading):", anchor='w')
        base_lbl = ttk.Label(test_frm, text="Default baseline (psi):", anchor='w')
        pump_lbl = ttk.Label(test_frm, text="Default pump:", anchor='w')
        dir_lbl = ttk.Label(test_frm, text="Project folder:", anchor='w')

        # the entries
        self.fail_psi = ttk.Spinbox(
            test_frm,
            from_=0,
            to=5000,
            width=30,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.time_limit = ttk.Spinbox(
            test_frm,
            from_=0,
            to=1440,
            width=30,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.interval = ttk.Spinbox(
            test_frm,
            from_=1,
            to=60,
            width=30,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.base_psi = ttk.Spinbox(
            test_frm,
            from_=0,
            to=5000,
            width=30,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.def_pump = ttk.Combobox(
            test_frm,
            values=["PSI 1", "PSI 2"],
            state='readonly',
            width=29
        )
        self.proj_dir = ttk.Entry(
            test_frm,
            width=32,
        )

        # grid everything
        psi_lbl.grid(row=0, column=0, sticky='e')
        self.fail_psi.grid(row=0, column=1, pady=2, padx=2, sticky='w')
        time_lbl.grid(row=1, column=0, sticky='e')
        self.time_limit.grid(row=1, column=1, pady=2, padx=2, sticky='w')
        int_lbl.grid(row=2, column=0, sticky='e')
        self.interval.grid(row=2, column=1, pady=2, padx=2, sticky='w')
        base_lbl.grid(row=3, column=0, sticky='e')
        self.base_psi.grid(row=3, column=1, pady=2, padx=2, sticky='w')
        pump_lbl.grid(row=4, column=0, sticky='e')
        self.def_pump.grid(row=4, column=1, pady=2, padx=2, sticky='w')
        dir_lbl.grid(row=5, column=0, sticky='e')
        self.proj_dir.grid(row=5, column=1, pady=2, padx=2, sticky='w')

        # frame for report settings
        rep_frm = tk.LabelFrame(self, text="Report Settings", font=bold_font)

        # the labels
        temp_lbl = ttk.Label(rep_frm, text="Report template:", anchor='w')
        color_lbl = ttk.Label(rep_frm, text="Color cycle:", anchor='w')

        # the entries
        self.temp_path = ttk.Entry(rep_frm, width=32)
        self.color_cycle = tk.Text(rep_frm, wrap='word', width=24, height=10)

        # grid everything
        temp_lbl.grid(row=0, column=0, padx=(77, 0), sticky='e')
        self.temp_path.grid(row=0, column=1, pady=2, padx=2, sticky='w')
        color_lbl.grid(row=1, column=0, sticky='e')
        self.color_cycle.grid(row=1, column=1, pady=2, padx=2, sticky='w')

        # grid the container frames
        test_frm.grid(row=0, column=0, sticky='nsew', pady=2, padx=2)
        rep_frm.grid(row=1, column=0, sticky='nsew', pady=2, padx=2)

    def fill_form(self):
        """Fill the form with values from the ConfigParser."""
        fail_psi = self.parser.getint('test settings', 'fail psi')
        time_limit = self.parser.getint('test settings', 'time limit minutes')
        interval = self.parser.getint('test settings', 'interval seconds')
        base_psi = self.parser.getint('test settings', 'default baseline')
        def_pump = self.parser.get('test settings', 'default pump')
        proj_dir = self.parser.get('test settings', 'project folder')
        temp_path = self.parser.get('report settings', 'template path')
        color_cycle = self.parser.get('report settings', 'color cycle')

        self.fail_psi.delete(0, 'end')
        self.time_limit.delete(0, 'end')
        self.interval.delete(0, 'end')
        self.base_psi.delete(0, 'end')
        self.proj_dir.delete(0, 'end')
        self.temp_path.delete(0, 'end')
        self.color_cycle.delete(1.0, 'end')

        self.fail_psi.insert(0, fail_psi)
        self.time_limit.insert(0, time_limit)
        self.interval.insert(0, interval)
        self.base_psi.insert(0, base_psi)
        self.def_pump.set(def_pump)
        self.proj_dir.insert(0, proj_dir)
        self.temp_path.insert(0, temp_path)
        self.color_cycle.insert(1.0, color_cycle)

    def close_settings(self):
        """Close the window."""
        pass

    def is_numeric(self, P):
        """Validate that user input is numeric."""
        if str.isdigit(P) or P == "":
            return True
        else:
            return False