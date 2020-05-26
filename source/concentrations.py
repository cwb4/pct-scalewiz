"""A simple calculator for determining treating volumes."""

import os
import tkinter as tk
from tkinter import ttk, font  # type: ignore


class ConcCalc(tk.Toplevel):
    """Simple Toplevel for calculating treating volumes."""

    def __init__(self, parent, *args, **kwargs):
        """Init the calculator."""
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        if os.name == 'nt':
            self.iconbitmap('chem.ico')
        self.winfo_toplevel().title('Concentration Calculator')
        self.conc = tk.IntVar()
        self.conc.trace('w', self.calc)

        self.vol = tk.IntVar()
        self.vol.trace('w', self.calc)

        self.mL = tk.StringVar()
        self.uL = tk.StringVar()

        self.build()

    def build(self):
        """Make the widgets."""
        tk.Label(
            self,
            text="Treating conc. (ppm): ",
            anchor='w'
        ).grid(row=0, column=0, padx=15, pady=3, sticky='w')
        tk.Label(
            self,
            text="Sample volume (mL): ",
            anchor='w'
        ).grid(row=1, column=0, padx=15, pady=3, sticky='w')

        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')

        tk.Label(
            self,
            text="Treating volume: ",
            anchor='w'
        ).grid(row=2, column=0, padx=15, pady=3, sticky='w')
        self.conc_ent = ttk.Entry(self, textvariable=self.conc)
        self.vol_ent = ttk.Entry(self, textvariable=self.vol)
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
            conc = int(self.conc_ent.get())
            vol = int(self.vol_ent.get())
            self.mL.set(f"{conc*vol/1000/1000:.4f} mL, or")
            self.uL.set(f"{conc*vol/1000:.2f} μL")
        except ValueError:
            pass


if __name__ == '__main__':
    root = tk.Tk()
    ConcCalc(root)
    root.mainloop()
