"""A custom tkinter widget to read/write ConfigParser objects from/to .ini files
"""

import configparser
import os
import tkinter as tk
from tkinter import scrolledtext, ttk

class ConfigManager(tk.Toplevel):

    DEFAULT_DICT = {
        'section1': {'key1': 'value1',
                     'key2': 'value2',
                     'key3': 'value3'},
        'section2': {'keyA': 'valueA',
                     'keyB': 'valueB',
                     'keyC': 'valueC'},
        'section3': {'foo': 'x',
                     'bar': 'y',
                     'baz': 'z'}
    }

    def __init__(self, parent, configpath=None,
            _title=' ', defaultdict=None
    ):
        """Pass in an absolute file path when you make a new instance.
             * _title: optional, the Toplevel's title.
             * defaultdict: dict to use when resetting defaults
                uses a demo dict for defaults if one isn't passed.

        To change some of the GUI elements dynamically change a
        self._attribute, destroy self.container and call self.build()
        """
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.minsize(400, 370)  # big enough to hold the DEFAULT_DICT

        self.config_path = configpath  # to config.ini
        self.window_title  = _title  # title of the Toplevel
        self.defaultdict = defaultdict
        # the string length threshold for using Entry/Text widget
        self.max_entry_length = 65
        self.text_width = 28  # width of text widgets
        self.text_height = 6  # height of text widgets
        self.entry_width = 40  # width of entry widgets
        self.label_width = 15  # width of label widgets


        if not self.config_path is None:
            self.config_path = os.path.normpath(configpath)
        if defaultdict is None:
            self.defaultdict = ConfigManager.DEFAULT_DICT
        if _title is None:
            self.window_title  = ' '

        self.build()

    def build(self):
        """Dynamically populates GUI from the contents of configpath"""
        self._sections = []  # list of all the sections
        self._section_keys = []  # list of keys from every section
        self._fields = []  # list of the input widgets from every section
        # assess the parser dict
        parser = configparser.ConfigParser()
        try:
            parser.read(self.config_path)
        except TypeError as e:
            parser.read_dict(self.defaultdict)
            self._sections = ['section1', 'section2', 'section3']
            self._section_keys = []
            for section in self._sections:
                self._section_keys.extend(parser[section].keys())

        self.parser_dict = self.as_dict(parser)

        #----------------------------- Cosmetics ---------------------------
        self.winfo_toplevel().title(self.window_title)
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

                tk.Label(frm,
                    text=key.title(),
                    anchor='ne',
                    width=self.label_width
                ).grid(row=idx, column=0, padx=2, pady=2, sticky='e')

                # if the key has a long value put it in a scrolledtext
                if len(self.parser_dict[section][key]) >= self.max_entry_length:
                    ent = tk.scrolledtext.ScrolledText(frm,
                        width=self.text_width,
                        height=self.text_height
                    )
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(1.0, self.parser_dict[section][key])

                else:  # use an entry widget if the key's value is short enough
                    ent =  ttk.Entry(frm, width=self.entry_width)
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
            ).grid(row=0, column=0, pady=5, padx=3, sticky='ne')
        ttk.Button(btnfrm,
            text='Reset Defaults',
            command=lambda: self.reset_config()
            ).grid(row=0, column=1, pady=5, padx=3, sticky='nw')
        btnfrm.pack()

        # pack everything else
        self.canvas.create_window((0, 0),
            window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.container.pack(fill="both", expand=True)

        # set bindings to enable scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind_all(
            '<MouseWheel>',
            lambda event: self.canvas.yview_scroll(
                int(-1*(event.delta/120)), "units"
            )
        )

    def reset_config(self):
        if not self.config_path is None:
            os.remove(self.config_path)
            # generate a fresh config
            # (...)
            pass

        # then rebuild the window
        self.container.destroy()
        self.build()

    def save_config(self):
        # collect all the inputs
        all_inputs = []
        # [print(i) for i in self._fields]
        for child in self._fields:  # filter getting by widget class
            if isinstance(child, ttk.Entry):
                all_inputs.append(child.get())
            if isinstance(child, tk.scrolledtext.ScrolledText):
                all_inputs.append(child.get(1.0, 'end'))

        new_parser_dict = {}
        for section in self._sections:
            new_parser_dict[section] = {}
            for section_key, input in zip(self._section_keys, all_inputs):
                if section_key in self.parser_dict[section]:
                    # configparser uses ordereddicts by default
                    # this should maintain their order
                    new_parser_dict[section][section_key] = input

        parser = configparser.ConfigParser()
        parser.read_dict(new_parser_dict)

        if not self.config_path is None:
            with open(self.config_path, 'w') as configfile:
                parser.write(configfile)

        # reset the form
        self.container.destroy()
        self.build()

    def as_dict(self, config) -> dict:
        """
        Converts a ConfigParser object into a dictionary.

        The resulting dictionary has sections as keys which point to a dict of the
        sections options as key : value pairs.

        https://stackoverflow.com/a/23944270
        """
        the_dict = {}
        for section in config.sections():
            the_dict[section] = {}
            for key, val in config.items(section):
                the_dict[section][key] = val
        return the_dict

if __name__ == '__main__':
    root = tk.Tk()
    ConfigManager(root)
    root.mainloop()
