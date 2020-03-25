class PlotUtil(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.build()

    def askfil(self, event):
        fil = filedialog.askopenfilename(initialdir = "C:\"",title="Select data output directory:", filetypes=[("CSV files", "*.csv")])
        event.widget.delete(0,tk.END)
        event.widget.insert(0,fil)
        event.widget.after(50, event.widget.xview_moveto, 1)  # BUG:  for some reason this only fires if postponed
        # https://stackoverflow.com/questions/29334544/why-does-tkinters-entry-xview-moveto-fail

    def build(self):
        self.winfo_toplevel().title("Plotting Utility")
        self.serfrm = tk.Frame(self)
        self.npltfrm = tk.Frame(self)

        fields = ["ser0", "ser1", "ser2", "ser3", "ser4", "ser5", "ser6", "ser7", "ser8", "ser9"]
        self.paths = [ttk.Entry(self.serfrm, width=35) for _ in fields]
        self.titles = [ttk.Entry(self.serfrm) for _ in fields]
        self.series = list(zip(self.paths, self.titles))
        tk.Label(self.serfrm, text="File path:").grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.serfrm, text="Series title:").grid(row=0, column=1, sticky=tk.W)
        for i, (path, title) in enumerate(self.series):
            path.grid(row=i+1, column=0, padx=3, pady=2)
            path.bind("<Button-1>", self.askfil)
            title.grid(row=i+1, column=1, padx=3, pady=2)
        self.anchorent = ttk.Entry(self.serfrm)
        self.locent = ttk.Entry(self.serfrm)
        tk.Label(self.serfrm, text="bbox_to_anchor:").grid(row=12, column=1)
        tk.Label(self.serfrm, text="loc:").grid(row=12, column=0)
        self.locent.grid(row=13, column=0, pady=(0,3)) # TODO: this spacing??
        self.anchorent.grid(row=13, column=1)
        self.pltbtn = ttk.Button(self.serfrm, text="Plot", width=35, command = self.make_plot)
        self.pltbtn.grid(row=14, column=0, columnspan=3)
        self.serfrm.pack(side=tk.LEFT)

    def make_plot(self):
        self.pltsrs={}
        for _, (path,title) in enumerate(self.series):
            self.pltsrs[path.get()] = title.get()
        if '' in self.pltsrs:
            del self.pltsrs['']
        print(self.pltsrs)

        fig, ax = plt.subplot()
        ax.plot()
