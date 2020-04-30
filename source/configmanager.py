"""A Tkinter widget to read/write ConfigParser objects from/to .ini files.

Uses a demo dict for example purposes if run as __main__
To change some of the GUI elements dynamically change a
instance._attribute, and call instance.build()

Args:
    * parent : the Tkinter parent
    * configpath : absolute path to config file to be edited, default is None
    * _title : title to use for the Toplevel, default is ' '
    * defaultdict : dict to use when resetting form to default values

Class variables:
    * ConfigManager.DEFAULT_DICT : used as fallback if a defaultdict isn't
     passed; can be changed

Methods:
    * ConfigManager.build(dict) -> None: rebuild form using the passed dict
    * ConfigManager.reset_config() -> None: rebuild form using the defaultdict
    * ConfigManager.save_config() -> None: scrapes the form into a ConfigParser
     object and saves it to configpath if one was given
    * ConfigManager.as_dict(ConfigParser) -> dict : returns ConfigParser object
     as a dict

Notes:
    * tries to treat very long dict values as lists if they contain commas;
     the contents are returned to string when writing to file. see line 146

"""


import configparser
import os
import tkinter as tk
from tkinter import scrolledtext, ttk


class ConfigManager(tk.Toplevel):
    # used if one isn't passed to the instance
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

    def __init__(
        self, parent,
        configpath=None, _title=' ', defaultdict=None
    ):
        """Initializes a new ConfigManager.
            * parent: should be a Tkinter object
            * configpath =  an absolute path to the config file
            * _title: optional, the Toplevel's title
            * defaultdict: dict to use when resetting defaults
             uses a demo dict for defaults if one isn't passed.
        """
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.minsize(400, 370)  # big enough to hold the DEFAULT_DICT
        self.configpath = configpath  # to config.ini
        if not self.configpath is None:
            self.configpath = os.path.normpath(configpath)
        self.window_title  = _title  # title of the Toplevel
        self.defaultdict = defaultdict
        if defaultdict is None:
            self.defaultdict = ConfigManager.DEFAULT_DICT

        # ------------------------Widget options-------------------------------
        # the string length threshold for using Entry/Text widget
        self.max_entry_length = 65
        self.text_width = 28  # width of text widgets
        self.text_height = 10  # height of text widgets
        self.entry_width = 40  # width of entry widgets
        self.label_width = 15  # width of label widgets
        # ---------------------------------------------------------------------

        # assess the parser dict
        parser = configparser.ConfigParser()
        try:
            parser.read(self.configpath)
        except TypeError as e:
            print(e)
            print("Using the defaultdict instead")
            parser.read_dict(self.defaultdict)
        finally:
            parser_dict = self.as_dict(parser)
            self.build(parser_dict)

    def build(self, parser_dict: dict) -> None:
        """Dynamically populates GUI from the contents of parser_dict"""
        try:
            self.container.destroy()
        except AttributeError as e:
            print("Tried to destroy the window's container before it was made")

        self.parser_dict = parser_dict
        self._fields = []  # list of the input widgets from every section
        self._sections = self.parser_dict.keys()  # list of all the sections
        self._section_keys = []  # list of keys from every section
        for section in self._sections:
            self._section_keys.extend(self.parser_dict[section].keys())

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
            for idx, section_key in enumerate(self.parser_dict[section].keys()):
                self._section_keys.append(section_key)
                frm.grid_rowconfigure(idx, weight=1)

                tk.Label(frm,
                    text=section_key.title(),
                    anchor='ne',
                    width=self.label_width
                ).grid(row=idx, column=0, padx=2, pady=2, sticky='e')

                # the length of this particular value
                val_len = len(self.parser_dict[section][section_key])
                # if the key has a long value put it in a scrolledtext
                if val_len >= self.max_entry_length:
                    ent = tk.scrolledtext.ScrolledText(frm,
                        width=self.text_width,
                        height=self.text_height
                    )
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    the_key = self.parser_dict[section][section_key]
                    if ',' in the_key:  # check to see if the string is a list
                        the_key = the_key.split(',')
                        for word in (the_key):
                            ent.insert('end', word.strip())
                            if not word in the_key[-1]:
                                ent.insert('end', ',\n')
                    else:  # it isn't clearly a list, so just stick it in there
                        ent.insert(1.0, the_key.strip())
                # use an entry widget if the key's value is short enough
                else:
                    ent =  ttk.Entry(frm, width=self.entry_width)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='e')
                    ent.insert(0, self.parser_dict[section][section_key])
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
        btnfrm.pack()  # put them at the bottom of the form

        # then pack everything else
        self.canvas.create_window((0, 0),
            window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.container.pack(fill="both", expand=True)
# -------------------------------End Cosmetics---------------------------------

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
        """Rebuilds the ConfigManager from the defaultdict."""
        print('Rebuilding form from defaultdict')
        self.build(self.defaultdict)

    def save_config(self):
        """Saves the contents of the form to configpath if one was passed."""
        # collect all the inputs
        all_inputs = []
        for child in self._fields:  # filter getting by widget class
            if isinstance(child, ttk.Entry):
                all_inputs.append(child.get())
            if isinstance(child, tk.scrolledtext.ScrolledText):
                text = child.get(1.0, 'end')
                all_inputs.append(text)

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

        if self.configpath is None:
            print(f'Not saving to file because configpath is {self.configpath}')
        else:
            with open(self.configpath, 'w') as configfile:
                parser.write(configfile)

        # reset the form to reflect the changes
        self.build(new_parser_dict)

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
    root.menubar = tk.Menu(root)
    root.menubar.add_command(
        label='Settings',
        command=lambda: ConfigManager(root)
    )
    root.winfo_toplevel().config(menu=root.menubar)
    root.winfo_toplevel().title('ConfigManager Demo')
    tk.Label(root,
        text='Your stuff here', anchor='center'
        ).grid(padx=100, pady=10)
    root.mainloop()
