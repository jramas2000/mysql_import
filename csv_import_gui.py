import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
import mysql.connector
from csv_import_mysqldb import csv_table_import

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', s)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled')
    def flush(self):
        pass

class CSVImportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('CSV to MySQL Importer')
        self.csv_folder = tk.StringVar()
        self.host = tk.StringVar(value='localhost')
        self.port = tk.StringVar(value='3306')
        self.user = tk.StringVar()
        self.password = tk.StringVar()
        self.database = tk.StringVar()
        self.clean_table_name = tk.BooleanVar(value=True)
        self.drop_table = tk.BooleanVar(value=True)
        self.create_table = tk.BooleanVar(value=True)
        self.load_data = tk.BooleanVar(value=True)
        self._build_gui()

    def _build_gui(self):
        # Dark mode colors
        bg = '#23272e'
        fg = '#f8f8f2'
        entry_bg = '#2d323b'
        entry_fg = '#f8f8f2'
        btn_bg = '#44475a'
        btn_fg = '#f8f8f2'
        warn_fg = '#ffb86c'
        check_bg = bg
        check_fg = fg
        scrollbar_bg = '#23272e'
        scrollbar_trough = '#2d323b'

        self.root.configure(bg=bg)
        frm = tk.Frame(self.root, bg=bg)
        frm.pack(padx=10, pady=10, fill='x')

        # Warning label
        warn_lbl = tk.Label(frm, text='Warning: This tool does not identify or set primary and foreign keys in tables.', fg=warn_fg, bg=bg, font=('Arial', 10, 'bold'))
        warn_lbl.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 10))

        # CSV Folder
        tk.Label(frm, text='CSV Folder:', fg=fg, bg=bg).grid(row=1, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.csv_folder, width=50, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=1, column=1, sticky='w')
        tk.Button(frm, text='Browse', command=self.browse_folder, bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg).grid(row=1, column=2, padx=5)

        # MySQL Params
        tk.Label(frm, text='Host:', fg=fg, bg=bg).grid(row=2, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.host, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=2, column=1, sticky='w')
        tk.Label(frm, text='Port:', fg=fg, bg=bg).grid(row=3, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.port, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=3, column=1, sticky='w')
        tk.Label(frm, text='User:', fg=fg, bg=bg).grid(row=4, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.user, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=4, column=1, sticky='w')
        tk.Label(frm, text='Password:', fg=fg, bg=bg).grid(row=5, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.password, show='*', bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=5, column=1, sticky='w')
        tk.Label(frm, text='Database:', fg=fg, bg=bg).grid(row=6, column=0, sticky='e')
        tk.Entry(frm, textvariable=self.database, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg).grid(row=6, column=1, sticky='w')

        # Options
        tk.Checkbutton(frm, text='Clean Table Name', variable=self.clean_table_name, bg=check_bg, fg=check_fg, selectcolor=entry_bg, activebackground=check_bg, activeforeground=check_fg).grid(row=7, column=0, sticky='w')
        tk.Checkbutton(frm, text='Drop Table', variable=self.drop_table, bg=check_bg, fg=check_fg, selectcolor=entry_bg, activebackground=check_bg, activeforeground=check_fg).grid(row=7, column=1, sticky='w')
        tk.Checkbutton(frm, text='Create Table', variable=self.create_table, bg=check_bg, fg=check_fg, selectcolor=entry_bg, activebackground=check_bg, activeforeground=check_fg).grid(row=8, column=0, sticky='w')
        tk.Checkbutton(frm, text='Load Data', variable=self.load_data, bg=check_bg, fg=check_fg, selectcolor=entry_bg, activebackground=check_bg, activeforeground=check_fg).grid(row=8, column=1, sticky='w')

        # Run Button
        tk.Button(frm, text='Start Import', command=self.start_import, bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg).grid(row=9, column=0, columnspan=3, pady=10)

        # Output with dark ttk.Scrollbar
        output_frame = tk.Frame(self.root, bg=bg)
        output_frame.pack(padx=10, pady=10, fill='both', expand=True)

        style = ttk.Style()
        style.theme_use('default')
        style.configure('Vertical.TScrollbar',
                        background=scrollbar_bg,
                        troughcolor=scrollbar_trough,
                        bordercolor=scrollbar_bg,
                        arrowcolor=fg)
        style.map('Vertical.TScrollbar',
                  background=[('active', btn_bg), ('!active', scrollbar_bg)])

        self.output = tk.Text(output_frame, width=80, height=20, state='disabled', bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, selectbackground='#44475a', selectforeground=entry_fg)
        self.output.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(output_frame, orient='vertical', command=self.output.yview, style='Vertical.TScrollbar')
        scrollbar.pack(side='right', fill='y')
        self.output['yscrollcommand'] = scrollbar.set

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.csv_folder.set(folder)

    def start_import(self):
        t = threading.Thread(target=self.run_import)
        t.start()

    def run_import(self):
        self.set_output('--- Starting Import ---\n')
        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = TextRedirector(self.output)
        sys.stderr = TextRedirector(self.output)
        try:
            conn = mysql.connector.connect(
                host=self.host.get(),
                port=int(self.port.get()),
                user=self.user.get(),
                password=self.password.get(),
                database=self.database.get(),
                allow_local_infile=True
            )
            null_chars = [np.nan, pd.NA, " ", ' ', "NaN",'NaN', '.']
            conditions = [self.clean_table_name.get(), self.drop_table.get(), self.create_table.get(), self.load_data.get()]
            csv_table_import(self.csv_folder.get(), conn, conditions, null_chars)
            print('--- Import Complete! ---')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def set_output(self, text):
        self.output.config(state='normal')
        self.output.insert('end', text)
        self.output.see('end')
        self.output.config(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    app = CSVImportGUI(root)
    root.mainloop() 