"""A Toplevel to manage settings from a ConfigParser object."""

import os
from configparser import ConfigParser
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import font  # type: ignore
import webbrowser

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
        'color cycle': """orange, blue, red, mediumseagreen, darkgoldenrod, indigo, mediumvioletred, darkcyan, maroon, darkslategrey"""
    }
}


def make_config(parser: ConfigParser):
    """Create a default scalewiz.ini in the current working directory."""
    parser.read_dict(DEFAULT_DICT)  # type: ignore
    with open('scalewiz.ini', 'w') as configfile:
        parser.write(configfile)


class ConfigManager(tk.Toplevel):
    """Toplevel for managing settings in an .ini file."""

    def __init__(self, parent, parser: ConfigParser):
        """Init with another Tk as parent."""
        tk.Toplevel.__init__(self, parent)
        self.parser = parser
        self.title('Settings')
        if os.name == 'nt':
            self.iconbitmap('chem.ico')
        self.build()
        self.fill_form()

    def build(self):
        """Make all the widgets."""
        # setup
        vcmd = (self.register(self.is_numeric))
        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')
        hyperlink_font = font.Font(font=def_font)
        hyperlink_font.config(underline=1)
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
            background='white',
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
        color_lbl = tk.Label(rep_frm, text="Color cycle:", anchor='w', font=hyperlink_font, fg='#0000EE')

        # the entries
        self.temp_path = ttk.Entry(rep_frm, width=32)
        self.color_cycle = tk.Text(rep_frm, wrap='word', width=32, height=10, font=font.nametofont("TkDefaultFont"))

        # grid everything
        temp_lbl.grid(row=0, column=0, padx=(77, 0), sticky='e')
        self.temp_path.grid(row=0, column=1, pady=2, padx=2, sticky='w')
        color_lbl.grid(row=1, column=0, sticky='ne')
        self.color_cycle.grid(row=1, column=1, pady=2, padx=2, sticky='w')

        # frame for buttons
        btn_frm = tk.Frame(self)

        # buttons
        save_btn = ttk.Button(btn_frm, text="Save", command=lambda: self.save_settings())
        reset_btn = ttk.Button(btn_frm, text="Restore Defaults", command=lambda: self.restore_defaults())

        # grid the buttons
        reset_btn.grid(row=0, column=0, padx=5, sticky='ew')
        save_btn.grid(row=0, column=1, padx=5, sticky='ew')
        for col in (0, 1):
            btn_frm.grid_columnconfigure(col, weight=1)

        # grid the container frames
        test_frm.grid(row=0, column=0, sticky='nsew', pady=2, padx=2)
        rep_frm.grid(row=1, column=0, sticky='nsew', pady=2, padx=2)
        btn_frm.grid(row=2, column=0, sticky='nsew', pady=2, padx=2)

        # widget bindings
        self.proj_dir.bind('<Button-1>', self.ask_dir)
        self.temp_path.bind('<Button-1>', self.ask_fil)
        color_lbl.bind('<Button-1>', lambda e: webbrowser.open_new(r'https://htmlcolorcodes.com/color-names/'))


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

    def save_settings(self):
        """Save the form contents to file."""
        self.parser['test settings']['fail psi'] = self.fail_psi.get()
        self.parser['test settings']['time limit minutes'] = self.time_limit.get()
        self.parser['test settings']['interval seconds'] = self.interval.get()
        self.parser['test settings']['default baseline'] = self.base_psi.get()
        self.parser['test settings']['default pump'] = self.def_pump.get()
        self.parser['test settings']['project folder'] = self.proj_dir.get()
        self.parser['report settings']['template path'] = self.temp_path.get()
        self.parser['report settings']['color cycle'] = self.color_cycle.get(1.0, 'end')
        with open('scalewiz.ini', 'w') as configfile:
            self.parser.write(configfile)

    def restore_defaults(self):
        """Fill the form with the DEFAULT_DICT."""
        self.parser.read_dict(DEFAULT_DICT)  # type: ignore
        self.fill_form()

    def ask_dir(self, event):
        """Create a prompt asking the user for a directory.

        If the path isn't
        blank, put it in the clicked widget.

        """
        dir = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select project folder:",
        )
        if dir != "":
            event.widget.delete(0,'end')
            event.widget.insert(0, dir)
            event.widget.after(75, event.widget.xview_moveto, 1)

    def ask_fil(self, event):
        """Create a prompt asking the user for an .xlsx file.

        If the path isn't
        blank, put it in the clicked widget.

        """
        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select report template:",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not fil == "":
            event.widget.delete(0, 'end')
            event.widget.insert(0, fil)
            event.widget.after(75, event.widget.xview_moveto, 1)

    def is_numeric(self, P):
        """Validate that user input is numeric."""
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
