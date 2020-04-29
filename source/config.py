import configparser
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


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
        self.winfo_toplevel().title('Settings')
        # self.geometry('500x510')

        self.manager = configparser.ConfigParser()
        self.manager.read('config.ini')
        config = as_dict(self.manager)

        # self.container = ttk.Frame(self)
        # self.canvas = tk.Canvas(self.container)
        # self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        # self.scrollable_frame = ttk.Frame(self.canvas)
        #
        # self.scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: self.canvas.configure(
        #         scrollregion=self.canvas.bbox("all")
        #     )
        # )
        #
        # self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame = tk.Frame(self)
        for section in config.keys():
            frm = tk.LabelFrame(self.scrollable_frame, text=section)
            lengths = [len(config[section][key]) for key in config[section].keys()]
            max_len = max(lengths)

            for idx, key in enumerate(config[section].keys()):
                frm.grid_rowconfigure(idx, weight=1)
                frm.grid_columnconfigure(1, weight=1)
                label = tk.Label(frm, text=key)
                label.grid(row=idx, column=0, padx=2, pady=2, sticky='ne')
                if len(config[section][key]) > 65:
                    ent = tk.scrolledtext.ScrolledText(frm, width=40, height=3)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='nw')
                    ent.insert(1.0, config[section][key])
                else:
                    if max_len > 65:
                        max_len = 65
                    ent =  ttk.Entry(frm, width=40)
                    ent.grid(row=idx, column=1, padx=2, pady=2, sticky='nw')
                    ent.insert(0, config[section][key])

            frm.pack(pady=5, padx=5, anchor='sw', fill='both', expand=True)

        self.scrollable_frame.pack()
        # self.canvas.pack(side="left", fill="both", expand=True)
        # self.scrollbar.pack(side="right", fill="y")
        # self.container.pack(fill="both", expand=True)


if __name__ == '__main__':
    window = tk.Tk()
    ConfigManager(window)
    window.mainloop()
