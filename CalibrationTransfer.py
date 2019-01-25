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

sheet = first.get_sheet_by_name('ABS')

spegg1 = list(range(sheet.max_columns)

for i in range(1,sheet.max_rows+1):
    for j in range(1, sheet.max_columns+1):
    spegg1[i].append(sheet(i, j).value)

print(spegg1)