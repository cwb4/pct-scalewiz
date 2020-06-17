"""A simple calculator for determining treating volumes."""

import tkinter as tk
from tkinter import ttk, font, TclError  # type: ignore

from iconer import set_window_icon


def is_numeric(val):
    """Validate that user input is numeric."""
    print(val)
    parts = val.split('.')
    print(parts)
    results = []
    for chars in parts:
        print(chars)
        print(str.isdigit(chars))
        results.append(chars == "" or str.isdigit(chars))
    print(bool(results))
    return all(results)


class ClCalc(tk.Toplevel):
    """Simple Toplevel for calculating chloride concentration."""

    def __init__(self, parent, *args, **kwargs):
        """Init the calculator."""
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        set_window_icon(self)
        self.winfo_toplevel().title('Chloride Calculator')
        self.resizable(0, 0)

        self.titrated = tk.DoubleVar()
        self.sample = tk.DoubleVar()
        self.titrant = tk.DoubleVar()
        for var in (self.titrated, self.sample, self.titrant):
            var.trace('w', self.calc)
        self.chlorides = tk.StringVar()

        self.build()

    def build(self):
        """Make the widgets."""
        vcmd = (self.register(is_numeric))
        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')

        tk.Label(
            self,
            text="Titrated (mL): ",
            anchor='w'
        ).grid(row=0, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            self,
            text="Sample volume (mL): ",
            anchor='w'
        ).grid(row=1, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            self,
            text="Titrant conc. (N): ",
            anchor='w'
        ).grid(row=2, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            self,
            text="Chloride conc. (ppm): ",
            anchor='w'
        ).grid(row=3, column=0, padx=15, pady=3, sticky='e')

        self.titrated_ent = ttk.Spinbox(
            self,
            from_=0, to=999999,
            textvariable=self.titrated,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.sample_ent = ttk.Spinbox(
            self,
            from_=0, to=999999,
            textvariable=self.sample,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.titrant_ent = ttk.Spinbox(
            self,
            from_=0, to=999999,
            textvariable=self.titrant,
            validate='all', validatecommand=(vcmd, '%P')
        )

        self.titrated_ent.grid(row=0, column=1, padx=15, pady=3, sticky='w')
        self.sample_ent.grid(row=1, column=1, padx=15, pady=3, sticky='w')
        self.titrant_ent.grid(row=2, column=1, padx=15, pady=3, sticky='w')

        result = tk.Label(self, textvariable=self.chlorides, font=bold_font, anchor='w')
        result.grid(row=3, column=1, padx=15, pady=3, sticky='w')

        self.titrated.set(1)
        self.sample.set(10)
        self.titrant.set(0.282)

    def calc(self, *args):
        """Calculate the treating volume."""
        try:
            titrated = self.titrated.get()
            sample = self.sample.get()
            titrant = self.titrant.get()
            result = round(titrated * titrant * 35500 / sample)
            self.chlorides.set(f"{result:,} ppm")
        except ValueError:
            pass
        except ZeroDivisionError:
            pass
        except TclError:
            pass


if __name__ == '__main__':
    root = tk.Tk()
    ClCalc(root)
    root.withdraw()
    root.mainloop()
