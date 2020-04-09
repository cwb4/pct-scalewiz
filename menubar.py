import tkinter as tk
from plotter import Plotter

class MenuBar(tk.Frame):
    styles = [
        "bmh",
        "fivethirtyeight",
        "seaborn",
        "seaborn-colorblind",
        "seaborn-dark-palette",
        "seaborn-muted",
        "seaborn-notebook",
        "seaborn-paper",
        "seaborn-pastel",
        "tableau-colorblind10"
        ]

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.build()

    def build(self):
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self, tearoff=0)
        self.filemenu.add_command(
            label=self.parent.main.savepath.get(),
            command=self.askdir
            )
        self.pltmenu = tk.Menu(master=self, tearoff=0)
        self.pltstylmenu = tk.Menu(master=self, tearoff=1)
        for style in MenuBar.styles:
            self.pltstylmenu.add_command(
                label=style,
                command=lambda s=style: (self.parent.main.plotstyle.set(s))
                )

        self.pltmenu.add_command(label="Make new plot", command=self.new_plot)
        self.pltmenu.add_cascade(label="Set plot style", menu=self.pltstylmenu)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Plot", menu=self.pltmenu)
        self.parent.winfo_toplevel().config(menu=self.menubar)

    def askdir(self):
        out = filedialog.askdirectory(
            initialdir="C:\"",
            title="Select data output directory:"
            )

        if out == "":
            pass
        else:
            self.parent.main.savepath.set(out)
            p = self.parent.main.savepath.get().split('/')
            pp = p[-2] + " - " + p[-1]
            self.filemenu.entryconfig(index=1, label=pp)
            self.parent.main.project.set(pp)
            self.parent.winfo_toplevel().title(self.parent.main.project.get())
            # self.parent.root.title(self.parent.project.get())

    def new_plot(self):
        self.parent.plotter = Plotter(self)
