#Importing modules

import tkinter as tk
from tkinter import filedialog
from openpyxl import load_workbook
from matplotlib import pyplot as plt

root = tk.Tk()
file_path = filedialog.askopenfilenames(filetype = [("Excel File","*.xlsx")])

### loading workbooks and sheets

first = load_workbook(str(file_path[0]))
second = load_workbook(str(file_path[1]))

sheet1 = first['ABS']
sheet2 = second['ABS']

### scraping data

# Fills up a list with an entire row
def fill_list(sheet, r, start = 1, length=sheet1.max_column):
    """ Fills up a list with an entire row from the excel sheet.
    
        Take two mandatory arguments, the sheetname and the row you want to scrape.
        
    """
    vals = []
    for i in range(start, length+1): 
        vals.append(sheet.cell(r, i).value)
    return vals

x = fill_list(sheet1, 1, 7)
# x2 = fill_list(sheet2, 1, 7)

def fill_y(start, end, sheet): 
    length = end-start
    y_names = []
    y_vals = []
    for y in range(length):
        y_names.append(sheet.cell(start+y, 1).value)
        y_vals.append(fill_list(sheet, start+y-1,7))
    return y_names, y_vals

names, values = fill_y(2, 30, sheet1)
names2, values2 = fill_y(2, 30, sheet2)

# plt.plot(x, values[3], x2, values2[3])

from scipy.interpolate import interp1d
import numpy as np

f = interp1d(x, values[3])

plt.plot(x, values[3], 'o', x, f(x), '--')