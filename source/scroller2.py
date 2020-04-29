"""A custom tkinter widget for accessing ConfigParser objects"""

import configparser
import os
import tkinter as tk
from tkinter import scrolledtext

class ConfigManager(tk.Toplevel):
    def __init__(self, parent, configpath='config.ini', inplace=False, parser=None, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        # the string length threshold for using Entry/Text widget
        self._max_entry_length = 65
        self._text_width = 28
        self._text_height = 6
        self._entry_width = 40
        self._label_width = 15
        self._section_keys = []
        self._fields = []

        # if a parser object wasn't passed when constructing the class,
        # try to read one from file
        self.parser = configparser.ConfigParser()
        self.parser.read(self._config_path)
        self.parser_dict = self.as_dict(parser)
        self.build()

    def build(self):
        self.winfo_toplevel().title('ConfigManager')
        self.container = tk.Frame(self)
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(
            master=self.container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        # make a LabelFrame for each section in the ConfigParser
        for section in self.parser_dict.keys():
            frm = tk.LabelFrame(self.scrollable_frame, text=section.title())
            frm.grid_columnconfigure(0, weight=1)
            frm.grid_columnconfigure(1, weight=1)
            # make a label and Entry/Text widget for each key in the section
            for idx, key in enumerate(self.parser_dict[section].keys()):
                self._section_keys.append(key)
                frm.grid_rowconfigure(idx, weight=1)

                tk.Label(
                    master=frm,
                    text=key.title(),
                    anchor='ne',
                    width=self._label_width
                ).grid(row=idx, column=0, padx=2, pady=2, sticky='e')

                # if the key has a long value put it in a scrolledtext
                if len(self.parser_dict[section][key]) >= self._max_entry_length:
                    ent = tk.scrolledtext.ScrolledText(
                        master=frm,
                        width=self._text_width,
                        height=self._text_height
                    )
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(1.0, self.parser_dict[section][key])

                else:  # use an entry widget if the key's value is short enough
                    ent =  ttk.Entry(frm, width=40)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(0, self.parser_dict[section][key])
                # after deciding which to make, add to a list for convenience
                self._fields.append(ent)
            # finally, pack the LabelFrame for that section
            frm.pack(pady=5, padx=5, anchor='sw', fill='both', expand=True)

        # make buttons to save the form or reset to defaults
        btnfrm = tk.Frame(self.scrollable_frame)
        ttk.Button(btnfrm,
            text='Save',
            command=lambda: self.save_config()
            ).grid(row=0, column=0, pady=3, padx=3, sticky='ne')

        ttk.Button(btnfrm,
            text='Reset Defaults',
            command=lambda: self.reset_config()
            ).grid(row=0, column=1, pady=3, padx=3, sticky='nw')
        btnfrm.pack()

        # pack everything else
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.container.pack(fill="both", expand=True)

        # set bindings to enable scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind_all(
            '<MouseWheel>',
            lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        )

    def reset_config(self):
        # os.remove(self._config_path)
        # make generate a fresh config, then rebuild the window
        # (...)
        self.container.destroy()
        self.build()

    def save_config(self):
        all_inputs = []
        for child in self._fields:
            if isinstance(child, ttk.Entry):
                all_inputs.append(child.get())
            elif isinstance(child, tk.scrolledtext.ScrolledText):
                all_inputs.append(child.get(1.0, 'end'))

        new_parser_dict ={}
        for section in self._sections:
            for section_key, input in zip(self._section_keys, all_inputs):
                if section_key in self.parser_dict[section]:
                    new_parser_dict[section][section_key] = input

        parser = configparser.ConfigParser()
        parser.read_dict(new_parser_dict)

        if self.given_parser is None:  # we are working from file
            with open(self._config_path, 'w') as configfile:
                self.manager.write(configfile)
            # refresh the window to reflect the new values
            self.container.destroy()
            self.build()
        else:
            return parser

    def as_dict(self, config):
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
