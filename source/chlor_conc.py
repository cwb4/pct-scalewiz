"""A simple calculator concentrations and titrations."""

import tkinter as tk
from tkinter import ttk, font, TclError  # type: ignore
from iconer import set_window_icon


def is_numeric(val):
    """Validate that user input is numeric."""
    parts = val.split('.')
    results = []
    for chars in parts:
        print(chars)
        print(str.isdigit(chars))
        results.append(chars == "" or str.isdigit(chars))
    print(bool(results))
    return all(results)


class ChlorConc(tk.Toplevel):
    """Simple Toplevel for calculating treating volumes."""

    def __init__(self, parent, *args, **kwargs):
        """Init the calculator."""
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.winfo_toplevel().title('Concentrations & Chlorides')
        self.resizable(0, 0)
        set_window_icon(self)

        # concentrations
        self.conc = tk.DoubleVar()
        self.vol = tk.DoubleVar()
        for var in (self.conc, self.vol):
            var.trace('w', self.conc_calc)
        self.mL = tk.StringVar()
        self.uL = tk.StringVar()

        # chlorides
        self.titrated = tk.DoubleVar()
        self.sample = tk.DoubleVar()
        self.titrant = tk.DoubleVar()
        for var in (self.titrated, self.sample, self.titrant):
            var.trace('w', self.chlor_calc)
        self.chlorides = tk.StringVar()

        self.build()

    def build(self):
        """Make the widgets."""
        vcmd = (self.register(is_numeric))
        notebook = ttk.Notebook(self)
        conc_tab = tk.Frame(notebook)
        def_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(font=def_font)
        bold_font.config(weight='bold')

        tk.Label(
            conc_tab,
            text="Treating conc. (ppm): ",
            anchor='w'
        ).grid(row=0, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            conc_tab,
            text="Sample volume (mL): ",
            anchor='w'
        ).grid(row=1, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            conc_tab,
            text="Treating volume: ",
            anchor='w'
        ).grid(row=2, column=0, padx=15, pady=3, sticky='e')
        self.conc_ent = ttk.Spinbox(
            conc_tab,
            from_=0, to=999999,
            textvariable=self.conc,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.vol_ent = ttk.Spinbox(
            conc_tab,
            from_=0, to=999999,
            textvariable=self.vol, validate='all',
            validatecommand=(vcmd, '%P')
        )
        self.conc_ent.grid(row=0, column=1, padx=15, pady=3, sticky='w')
        self.vol_ent.grid(row=1, column=1, padx=15, pady=3, sticky='w')

        mL = tk.Label(conc_tab, textvariable=self.mL, font=bold_font, anchor='w')
        uL = tk.Label(conc_tab, textvariable=self.uL, font=bold_font, anchor='w')
        mL.grid(row=2, column=1, padx=15, pady=3, sticky='w')
        uL.grid(row=3, column=1, padx=15, pady=3, sticky='w')

        self.conc.set(100)
        self.vol.set(1000)

        notebook.add(conc_tab, text="Concentrations")

        chlor_tab = tk.Frame(notebook)

        tk.Label(
            chlor_tab,
            text="Titrated (mL): ",
            anchor='w'
        ).grid(row=0, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            chlor_tab,
            text="Sample volume (mL): ",
            anchor='w'
        ).grid(row=1, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            chlor_tab,
            text="Titrant conc. (N): ",
            anchor='w'
        ).grid(row=2, column=0, padx=15, pady=3, sticky='e')
        tk.Label(
            chlor_tab,
            text="Chloride conc. (ppm): ",
            anchor='w'
        ).grid(row=3, column=0, padx=15, pady=3, sticky='e')

        self.titrated_ent = ttk.Spinbox(
            chlor_tab,
            from_=0, to=999999,
            textvariable=self.titrated,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.sample_ent = ttk.Spinbox(
            chlor_tab,
            from_=0, to=999999,
            textvariable=self.sample,
            validate='all', validatecommand=(vcmd, '%P')
        )
        self.titrant_ent = ttk.Spinbox(
            chlor_tab,
            from_=0, to=999999,
            textvariable=self.titrant,
            validate='all', validatecommand=(vcmd, '%P')
        )

        self.titrated_ent.grid(row=0, column=1, padx=15, pady=3, sticky='w')
        self.sample_ent.grid(row=1, column=1, padx=15, pady=3, sticky='w')
        self.titrant_ent.grid(row=2, column=1, padx=15, pady=3, sticky='w')

        result = tk.Label(chlor_tab, textvariable=self.chlorides, font=bold_font, anchor='w')
        result.grid(row=3, column=1, padx=15, pady=3, sticky='w')

        self.titrated.set(1)
        self.sample.set(10)
        self.titrant.set(0.282)

        notebook.add(chlor_tab, text="Chlorides")

        notebook.pack()

    def conc_calc(self, *args):
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

    def chlor_calc(self, *args):
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
    ChlorConc(root)
    root.withdraw()
    root.mainloop()
