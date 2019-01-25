#Importing modules
import os
import tkinter as tk
from tkinter import filedialog
from openpyxl import load_workbook, Workbook


root = tk.Tk()
root.withdraw()
wb = Workbook()

#Grabbing the file pathes=[("E
file_path = filedialog.askopenfilenames(filetype = (["Excel File","*.xlsx"]))

#Importing workbook
first = load_workbook(str(file_path[0]))
second = load_workbook(str(file_path[1]))

# Making a separate file
# os.chdir(filedialog.askdirectory())
# cwd = os.getcwd()
# first.save('combined data.xlsx')

# third = load_workbook(cwd+'\\combined data.xlsx')

sheet = first.get_sheet_by_name('ABS')

first.save('Updated.xlsx')

