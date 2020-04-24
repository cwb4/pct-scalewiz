"""Unused code snippets"""

def export_report(self):
    """ Part of reporter
    Not implemented - too much trouble getting images in correctly """
    template_path = r"C:\Users\P\Documents\GitHub\pct-scalewiz\demo\sample_data\Report Template - Calcium Carbonate Scale Block Analysis.xlsx"
    project = self.mainwin.project.split('\\')
    sample_point = project[-1].split('-')[0]
    customer = project[-2]

    try:
        result_titles = self.results_queue[0]
        result_values = self.results_queue[1]
        durations = self.results_queue[2]
        baseline = self.results_queue[3]
    except AttributeError:
        # messagebox saying no data selected?
        pass


    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    ws['C4'] = customer
    ws['C7'] = sample_point
    ws['I7'] = f"{date.today()}"
    ws['D11'] = f"{baseline} psi"

    chem_name_cells = [f"A{i}" for i in range(19, 26)]
    chem_conc_cells = [f"D{i}" for i in range(19, 26)]
    duration_cells = [f"E{i}" for i in range(19, 26)]
    protection_cells = [f"H{i}" for i in range(19, 26)]


    chem_names = [title.split(' ')[0] for title in result_titles]
    chem_concs = [" ".join(title.split(' ')[1:2]) for title in result_titles]

    for (cell, name) in zip(chem_name_cells, chem_names):
        ws[cell] = name
    for (cell, conc) in zip(chem_conc_cells, chem_concs):
        ws[cell] = conc
    for (cell, duration) in zip(duration_cells, durations):
        ws[cell] = f"{round(duration/60, 2)}"
    for (cell, score) in zip(protection_cells, result_values):
        ws[cell] = score

    project = self.mainwin.project.split('\\')
    short_proj = project[-1]
    _img = f"{short_proj}.png"
    _path = os.path.join(self.mainwin.project, _img)
    # IImage.open(_path).save(_path)

    try:
        img = Image(_path)
        ws.add_image(img, 'A28')
    except FileNotFoundError as e:
        print(os.path.isfile(_path))
        print(e)


    report_name = f"{short_proj}.xlsx"
    report_path = os.path.join(self.mainwin.project, report_name)
    wb.save(filename=report_path)
    # messagebox to say successful

### this was in reporter.evaluate

    self.results_queue = (
        result_titles,
        result_values,
        durations,
        baseline,
        )

    ### this was in the same, before the for trial in trials block
    durations = [len(trial) for trial in trials]
