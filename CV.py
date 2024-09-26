import tkinter as tk
from tkinter import ttk
import yaml

import os
import re
import inspect

from pyhtml2pdf import converter
from bs4 import BeautifulSoup
from functools import partial
from datetime import datetime

# templates

def template_Title(content, params):
    title = params["Title"]
    if title: return title
    return "AWS Cloud Engineer"

def template_Company(content, params):
    return params["Company"]

def template_Job(content, params):
    job = params["Job"]
    if job: return job
    return "Cloud Engineer"

def template_Hr(content, params):
    hr = params["HR"]
    if hr: return hr
    return f"{template_Company(content, params)} Recruitment Team"

def template_Value(content, params):
    value = params["Value"]
    if value: return value
    return "innovation and continuous improvement"

def template_Bubbles(content, params):
    res = "\n".join([f"<span class='skill'>{bubble}</span>" for bubble in content.split(",")])
    res = f"<div class='skills'>{res}</div>"
    return res

def template_If(content, params):
    pars = content.split("|")
    if   len(pars) == 0:
        return ""
    elif len(pars) == 1:
        return pars[0]

    cond  = pars[0]
    case0 = pars[1]
    case1 = pars[2] if len(pars) == 3 else ""

    ret = case0 if cond in params and params[cond] != "" else case1

    return ret


# pdf

def get_functions():
    return {key: value for key, value in inspect.getmembers(__import__(__name__)) if inspect.isfunction(value)}

def camel_case_to_readable(string):
    readable = re.sub(r'(?<!^)(?=[A-Z])', ' ', string)
    readable = readable.replace("C V", "CV") # 0=)
    return readable

def apply_template(match, name, func, params):
    content = match.group(1)
    res = func(content, params)
    return res

def make_pdf(id, params, do_pdf = True):
    source = f'./templates/{id}/{id}.docx.html'
    source = os.path.abspath(source)


    with open(source, 'r', encoding='utf-8') as file:
        content = file.read()

    with open("style.html", 'r', encoding='utf-8') as file:
        style = file.read()

    content = content.replace("</head>", "</head>" + style, 1)

    prefix = "template_"
    funcs = [(name[len(prefix):], func) for name, func in get_functions().items() if name.startswith(prefix)]

    for open_smb, close_smb in [("(", ")"), ("[", "]"), ("{", "}"), ]:
        for name, func in funcs:
            template_partial = partial(apply_template, name=name, func=func, params=params)
            pattern = r"#{}{}(.*?){}".format(name, re.escape(open_smb), re.escape(close_smb))
            content = re.sub(pattern, template_partial, content, flags=re.DOTALL)

        # pattern = "#" + name + r"\((.*?)\)"
        # content = re.sub(pattern, template_partial, content)

    content = BeautifulSoup(content, 'html.parser')
    content = content.prettify()


    medi = f'./templates/{id}/{id}.html'
    medi = os.path.abspath(medi)


    with open(medi, 'w') as file:
        file.write(content)


    if do_pdf:
        medi = f'file:///{medi}'
        dest = f'./outputs/{camel_case_to_readable(id)}.pdf'

        print_options={
            "marginTop"   : 0,
            "marginBottom": 0,
            "marginLeft"  : 0,
            "marginRight" : 0,
        }
        converter.convert(medi, dest, print_options=print_options, install_driver=False)

    print("DevTools done")


# application

class App:

    def get_raw_data(self, i):
        row = {}
        for j in range(len(self.cols)):
            val = self.entries[i][j].get()
            # print(f"Cell ({i+1}, {j+1}): {val}")
            row[self.cols[j]] = val
        return row


    def get_current_row_number(self):
        widget = self.active_entry
        if widget:
            pass
        else:
            print("No active row found.")
            return None

        for i, row_entries in enumerate(self.entries):
            if widget in row_entries:
                row = i
                break
        
        return row

    def get_current_row(self):
        num = self.get_current_row_number()
        return self.get_raw_data(num)

    def save_data(self):
        res = []
        for i in range(len(self.entries)):
            row = self.get_raw_data(i)
            res.append(row)

        with open('data.yaml', 'w') as file:
            yaml.dump(res, file, default_flow_style=False, allow_unicode=True)

    def on_focus_in(self, event):
        self.active_entry = event.widget

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def __init__(self, root):
        self.root = root

        root.title("Table with Add Row and Print Active Row")
        root.geometry("800x600")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        table_frame = ttk.Frame(root)
        table_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(table_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.inner_table_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_table_frame, anchor="nw")

        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X)

        add_row_button = ttk.Button(button_frame, text="Add", command=self.add_row)
        add_row_button.pack(side=tk.LEFT, padx=10, pady=10)

        submit_button = ttk.Button(button_frame, text="Print", command=self.print_active_row)
        submit_button.pack(side=tk.LEFT, padx=10, pady=10)

        add_row_button = ttk.Button(button_frame, text="Documents", command=self.create_docs)
        add_row_button.pack(side=tk.LEFT, padx=10, pady=10)

        add_row_button = ttk.Button(button_frame, text="Today", command=self.set_today)
        add_row_button.pack(side=tk.LEFT, padx=10, pady=10)

        
        self.cols = ["Title", "Company", "Job", "HR", "Value", "Date"]
        self.entries = []
        with open('data.yaml', 'r') as file:
            data = yaml.safe_load(file)

        i = -1
        for row in data:
            i += 1

            row_entries = []
            j = -1
            for col in self.cols:
                j += 1

                entry = ttk.Entry(self.inner_table_frame)
                entry.grid(row=i, column=j, padx=1, pady=1)
                entry.bind("<FocusIn>", self.on_focus_in)
                if col in row:
                    entry.insert(0, row[col])

                row_entries.append(entry)

            self.entries.append(row_entries)

    def add_row(self):
        new_row = []
        row_index = len(self.entries)
        for j in range(len(self.cols)):
            entry = ttk.Entry(self.inner_table_frame)
            entry.grid(row=row_index, column=j, padx=5, pady=5)
            entry.bind("<FocusIn>", self.on_focus_in)
            new_row.append(entry)
        self.entries.append(new_row)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def print_active_row(self):
        row = self.get_current_row()

        print(f"Data from current row:")
        for key, value in row.items():
            print(f"  {key}: {value}") # self.entries[row][j].get()

    def create_docs(self):
        # make_pdf("PavelEreskoCV", self.get_current_row())
        # make_pdf("PavelEreskoCoverLetter", self.get_current_row())
        make_pdf("Test", self.get_current_row())
        print("docs created")

    def set_today(self):
        num = self.get_current_row_number()
        row = self.entries[num]
        # row[self.cols.index("Date")].set(datetime.today().strftime("%d.%m.%y"))

        entry = row[self.cols.index("Date")]
        entry.delete(0, 'end')
        entry.insert(0, datetime.today().strftime("%d.%m.%y"))
        

root = tk.Tk()
app = App(root)
root.mainloop()
