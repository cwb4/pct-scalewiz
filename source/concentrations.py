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


class ConcCalc(tk.Toplevel):
    """Simple Toplevel for calculating treating volumes."""

    def __init__(self, parent, *args, **kwargs):
        """Init the calculator."""
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        set_window_icon(self)
        self.winfo_toplevel().title('Concentration Calculator')
        self.resizable(0, 0)
        self.conc = tk.DoubleVar()
        self.conc.trace('w', self.calc)

        self.vol = tk.DoubleVar()
        self.vol.trace('w', self.calc)

        self.mL = tk.StringVar()
        self.uL = tk.StringVar()

        self.build()

    def build(self):
        """Make the widgets."""
        vcmd = (self.register(is_numeric))
        tk.Label(
            self,
            text="Treating conc. (ppm): ",
            anchor='w'
        ).grid(row=0, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            self,
            text="Sample volume (mL): ",
            anchor='w'
        ).grid(row=1, column=0, padx=15, pady=3, sticky='e')

        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')

        tk.Label(
            self,
            text="Treating volume: ",
            anchor='w'
        ).grid(row=2, column=0, padx=15, pady=3, sticky='e')
        self.conc_ent = ttk.Spinbox(
            self,
            from_=0, to=999999,
            textvariable=self.conc,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.vol_ent = ttk.Spinbox(
            self,
            from_=0, to=999999,
            textvariable=self.vol, validate='all',
            validatecommand=(vcmd, '%P')
        )
        self.conc_ent.grid(row=0, column=1, padx=15, pady=3, sticky='w')
        self.vol_ent.grid(row=1, column=1, padx=15, pady=3, sticky='w')

        mL = tk.Label(self, textvariable=self.mL, font=bold_font, anchor='w')
        uL = tk.Label(self, textvariable=self.uL, font=bold_font, anchor='w')
        mL.grid(row=2, column=1, padx=15, pady=3, sticky='w')
        uL.grid(row=3, column=1, padx=15, pady=3, sticky='w')

        self.conc.set(100)
        self.vol.set(1000)

    def calc(self, *args):
        """Calculate the treating volume."""
        try:
            conc = self.conc.get()
            vol = self.vol.get()
            self.mL.set(f"{conc*vol/1000/1000:.4f} mL, or")
            self.uL.set(f"{conc*vol/1000:.1f} μL")
        except ValueError:
            pass
        except ZeroDivisionError:
            pass
        except TclError:
            pass


if __name__ == '__main__':
    root = tk.Tk()
    ConcCalc(root)
    root.mainloop()
