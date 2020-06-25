"""Exports a report."""

from datetime import date
import os
import time
import tkinter as tk
from tkinter.messagebox import showinfo, showerror
import shutil
import openpyxl
import PIL

from iconer import set_window_icon


def ask_details(self, path):
    def return_details(widgets):
        details = [widget.get() for widget in widgets]
        details = [value.strip() for value in details]
        return details
        header_info.destroy()

    header_info = tk.Toplevel(self)
    header_info.attributes('-topmost', 'true')
    header_info.title('Project details')
    set_window_icon(header_info)
    comp_lbl = tk.Label(header_info, text="Company:", anchor='w')
    sample_lbl = tk.Label(header_info, text="Sample point:", anchor='w')
    cust_lbl = tk.Label(header_info, text="Customer:", anchor='w')
    client_lbl = tk.Label(header_info, text="Submitted by:", anchor='w')
    date_lbl = tk.Label(header_info, text="Date submitted:", anchor='w')

    comp_ent = tk.Entry(header_info)
    sample_ent = tk.Entry(header_info)
    cust_ent = tk.Entry(header_info)
    client_ent = tk.Entry(header_info)
    date_ent = tk.Entry(header_info)
    widgets = (comp_ent, sample_ent, cust_ent, client_ent, date_ent)

    submit_btn = tk.Button(header_info, text="Confirm", command=return_details(widgets))

    comp_lbl.grid(row=0, column=0, sticky='w')
    sample_lbl.grid(row=1, column=0, sticky='w')
    cust_lbl.grid(row=2, column=0, sticky='w')
    client_lbl.grid(row=3, column=0, sticky='w')
    date_lbl.grid(row=4, column=0, sticky='w')

    comp_ent.grid(row=0, column=1, sticky='e')
    sample_ent.grid(row=1, column=1, sticky='e')
    cust_ent.grid(row=2, column=1, sticky='e')
    client_ent.grid(row=3, column=1, sticky='e')
    date_ent.grid(row=4, column=1, sticky='e')

    submit_btn.grid(row=5, columnspan=2)

    project = path.split('\\')
    if len(project) >= 3:
        comp_ent.insert(0, project[-1].split('-')[0].strip())
        sample_ent.insert(0, project[-1].split('-')[1].strip())
        cust_ent.insert(0, project[-2].strip())


def export_report(self):
    """Export the reporter's results_queue to an .xlsx file."""
    if not hasattr(self, 'results_queue'):
        showinfo(
            parent=self,
            message="You must evaulate a set of data before exporting a report."
        )
        return
    template_path = self.parser.get('report settings', 'template path')
    if not os.path.isfile(template_path):
        showerror(
            parent=self,
            message="No valid template file found.\nYou can set the template path in Settings > Report Settings."
        )
        return
    details = ask_details(self, self.mainwin.project)
    print("Preparing export")
    start = time.time()
    company = details[0]
    sample = details[1]
    customer = details[2]
    client = details[3]
    sub_date = details[4]


    file = f"#-# {short_proj} Calcium Carbonate Scale Block Analysis.xlsx"
    report_path = os.path.join(self.mainwin.project, file)

    print(f"Copying report template to\n{report_path}")
    shutil.copyfile(template_path, report_path)

    print(f"Populating file\n{report_path}")
    workbook = openpyxl.load_workbook(report_path)
    ws = workbook.active

    img_filename = f"{short_proj}.png"
    img_path = os.path.join(self.mainwin.project, img_filename)
    print("Making temp resized plot image")
    try:
        img = PIL.Image.open(img_path)
        # img = img.resize((700, 265))
    except FileNotFoundError:
        print("Couldn't find the plot image file, aborting export")
        return
    img = img.resize((667, 257))
    img_path = img_filename[:-4]
    img_path += "- temp.png"
    img.save(img_path)
    img = openpyxl.drawing.image.Image(img_path)
    img.anchor = 'A28'
    ws._images[1] = img

    blank_times = self.results_queue[0]
    result_titles = self.results_queue[1]
    result_values = self.results_queue[2]
    durations = self.results_queue[3]
    baseline = self.results_queue[4]
    ylim = self.results_queue[5]
    max_psis = self.results_queue[6]

    ws['C4'] = customer
    ws['C6'] = company
    ws['C7'] = sample
    today = date.today().strftime("%B %d, %Y")
    ws['I7'] = f"{today}"
    ws['D11'] = f"{baseline} psi"
    ws['G16'] = round(ylim)

    print(f"customer: {customer}")
    print(f"company: {company}")
    print(f"well / sample point: {sample}")

    blank_time_cells = [f"E{i}" for i in range(16, 18)]
    chem_name_cells = [f"A{i}" for i in range(19, 27)]
    chem_conc_cells = [f"D{i}" for i in range(19, 27)]
    duration_cells = [f"E{i}" for i in range(19, 27)]
    max_psi_cells = [f"G{i}" for i in range(19, 27)]
    protection_cells = [f"H{i}" for i in range(19, 27)]

    chem_names = [" ".join(title.split(' ')[:-2]) for title in result_titles]
    chem_concs = [" ".join(title.split(' ')[-2:-1]) for title in result_titles]

    for (cell, blank_time) in zip(blank_time_cells, blank_times):
        ws[cell] = round(blank_time / 60, 2)
    for (cell, name) in zip(chem_name_cells, chem_names):
        ws[cell] = f"{name}"
    for (cell, conc) in zip(chem_conc_cells, chem_concs):
        ws[cell] = round(float(conc), 1)
    for (cell, duration) in zip(duration_cells, durations):
        ws[cell] = round(float(duration), 2)
    for (cell, psi) in zip(max_psi_cells, max_psis):
        ws[cell] = round(psi)
    for (cell, score) in zip(protection_cells, result_values):
        score = float(score[:-1])
        if score >= 100:
            score = 100
        ws[cell] = score / 100  # the template has conditional % formatting

    rows_with_data = [16, 17, *range(19, 27)]  # where the data is
    hide_rows = []  # rows we want to hide
    resize_rows = []  # rows we want to resize

    for i in rows_with_data:
        if ws[f'A{i}'].value is None:  # if the cell is empty
            hide_rows.append(i)  # add it to the list of rows to hide
        else:
            resize_rows.append(i)  # add it to the list of rows to reszie

    row_height = 200 / len(resize_rows)  # we have ~200px to work with total
    if row_height >= 30:  # we don't want any rows bigger than this
        row_height = 30
    for row in resize_rows:  # this does the resizing
        ws.row_dimensions[row].height = row_height
    for row in hide_rows:  # this hides the empty rows
        ws.row_dimensions[row].hidden = True

    print(f"Saving report to\n{report_path}")
    workbook.save(filename=report_path)
    print("Removing temp files")
    os.remove(img_path)
    print(f"Finished export in {round(time.time() - start, 2)} s")
    showinfo(
        parent=self,
        message=f"Report exported to\n{report_path}"
    )
