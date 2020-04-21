"""A custom tkinter widget for collecting user input"""

import tkinter as tk
from tkinter import ttk, filedialog


class SeriesEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.plotpump = tk.StringVar()
        self.plotpump.set("PSI 2")
        self.build()

    def build(self):
        """Make the widgets"""
        self.path = ttk.Entry(self, width=20)
        self.path.bind("<Button-1>", self.askfil)
        self.path.grid(row=0, column=0, padx=2, pady=1)

        self.title = ttk.Entry(self, width=25)
        self.title.grid(row=0, column=1, padx=2, pady=1)

        tk.Radiobutton(
            master=self,
            text="PSI 1",
            variable=self.plotpump,
            value='PSI 1'
            ).grid(row=0, column=2, padx=2, pady=1)

        tk.Radiobutton(
            master=self,
            text="PSI 2",
            variable=self.plotpump,
            value='PSI 2'
            ).grid(row=0, column=3, padx=2, pady=1)

        ttk.Button(
            master=self,
            text="Remove",
            command=self.clear_ents
            ).grid(row=0, column=4, padx=2, pady=2)

    def askfil(self, event):
        """Create a prompt asking the user for a csv file. If the path isn't
        blank, put it in the clicked widget, then move focus to the next entry
        """

        fil = filedialog.askopenfilename(
            initialdir="C:\"",
            title="Select data output directory:",
            filetypes=[("CSV files", "*.csv")]
            )

        # could probably just do with direct refs to self.path, but w/e
        if not fil == "":
            event.widget.delete(0, tk.END)
            event.widget.insert(0, fil)
            event.widget.after(50, event.widget.xview_moveto, 1)
            title = fil.split("/")[-1].replace('_', ' ')[:-4]
            evemt.widget.after(50, lambda: self.title.delete(0, tk.END))
            event.widget.after(50, lambda: self.title.insert(0, title))
            event.widget.after(50, lambda: self.title.focus_set())
        # NOTE: on use of after
        # https://stackoverflow.com/questions/29334544/

    def clear_ents(self):
        """Clears the widget's entry fields"""

        self.path.delete(0, tk.END)
        self.title.delete(0, tk.END)
