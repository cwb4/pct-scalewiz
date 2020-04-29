import configparser
import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext


def as_dict(config):
    """
    Converts a ConfigParser object into a dictionary.

    The resulting dictionary has sections as keys which point to a dict of the
    sections options as key => value pairs.

    https://stackoverflow.com/a/23944270
    """
    the_dict = {}
    for section in config.sections():
        the_dict[section] = {}
        for key, val in config.items(section):
            the_dict[section][key] = val
    return the_dict

class ConfigManager(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.core = parent.core
        self.winfo_toplevel().title('Settings')
        self.build()

    def build(self):
        self.manager = configparser.ConfigParser()
        self.manager.read('config.ini')
        self.config = as_dict(self.manager)
        self._sections = self.config.keys()
        self._section_keys = []
        self._fields = []

        self.container = tk.Frame(self)

        for section in self.config.keys():
            frm = tk.LabelFrame(self.container, text=section.title())
            frm.grid_columnconfigure(0, weight=2)
            frm.grid_columnconfigure(1, weight=1)
            lengths = [len(self.config[section][key]) for key in self.config[section].keys()]
            max_len = max(lengths)
            for idx, key in enumerate(self.config[section].keys()):
                frm.grid_rowconfigure(idx, weight=1)
                label = tk.Label(frm, text=key.title(), anchor='e', width=15)
                self._section_keys.append(key)
                label.grid(row=idx, column=0, padx=2, pady=2, sticky='e')
                if len(self.config[section][key]) > 65:
                    ent = tk.scrolledtext.ScrolledText(frm, width=28, height=6)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(1.0, self.config[section][key])
                else:
                    if max_len > 65:
                        max_len = 65
                    ent =  ttk.Entry(frm, width=40)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(0, self.config[section][key])
                self._fields.append(ent)
            frm.pack(pady=5, padx=5, anchor='sw', fill='both', expand=True)

        frm = tk.Frame(self.container)
        ttk.Button(frm,
            text='Save',
            command=lambda: self.save_config()
            ).grid(row=0, column=0, pady=3, padx=3, sticky='ne')

        ttk.Button(frm,
            text='Reset Defaults',
            command=lambda: self.reset_config()
            ).grid(row=0, column=1, pady=3, padx=3, sticky='nw')
        frm.pack()

        self.container.pack()

    def reset_config(self):
        os.remove('config.ini')
        self.core.make_config()
        self.container.destroy()
        self.build()

    def save_config(self):
        all_inputs = []
        for child in self._fields:
            if isinstance(child, ttk.Entry):
                all_inputs.append(child.get())
            elif isinstance(child, tk.scrolledtext.ScrolledText):
                all_inputs.append(child.get(1.0, 'end'))
        for section in self._sections:
            for section_key, input in zip(self._section_keys, all_inputs):
                if section_key in self.config[section]:
                    self.manager[section][section_key] = input

        with open('config.ini', 'w') as configfile:
            self.manager.write(configfile)
        self.container.destroy()
        self.build()
