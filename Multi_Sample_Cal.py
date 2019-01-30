#Importing modules

from tkinter import *
from tkinter import filedialog
from openpyxl import load_workbook
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline as spl
import numpy as np
from numpy import square as sq
from peakutils import indexes as peak


root = Tk()
file_path = filedialog.askopenfilenames(filetype = [("Excel File","*.xlsx")])

first = load_workbook(str(file_path[0]))
second = load_workbook(str(file_path[1]))

sheet1 = first['ABS']
sheet2 = second['ABS']

# Fills up a list with an entire row
def fill_list(sheet, r, start = 1, length=sheet1.max_column):
    vals = []
    for i in range(start, length+1): 
        vals.append(sheet.cell(r, i).value)
    return vals

# Saving a 1D array of the x-values of each instrument

def find_rcal():
    indexes = []
    for i in range(1, sheet1.max_column):
        if 'RCAL' in str(sheet1.cell(i, 1).value):
            indexes.append(i)
    return indexes

rcal_i = find_rcal()

first_x = fill_list(sheet1, 1, 7) 
first_x2 = fill_list(sheet2, 1, 7) 

first_row = [] # stores 3 sets of y-values for the calibration samples of the main instrument
first_row2 = [] # stores 3 sets of y-values for the calibration samples of the secondary instrument

y1 = []
y2 = []
yy1 = []
yy2 = []

x = [first_x[i] for i in range(50, 85)]

for i in rcal_i:
    first_row.append(fill_list(sheet1, i, 7))
    first_row2.append(fill_list(sheet2, i, 7))

for i in range(len(rcal_i)):
    y1.append(spl(first_x, first_row[i]))
    y2.append(spl(first_x2, first_row2[i]))
    yy1.append(y1[i](x))
    yy2.append(y2[i](x))


def shift(yy1, yy2):
    l = [] # array of the sum of squares
    shift_factor = np.linspace(-5, 5, 1001)
    
    for i in shift_factor:
        nx = x + i
        nyy2 = list(np.ones(len(yy2)))
        squaresum = []
        
        for j in range(len(yy2)): 
            ny2 = spl(nx, yy2[j]) # same shape
            nyy2[j] = ny2(x) # new y-values
            
            squaresum.append(sum(abs(sq(yy1[j])-sq(nyy2[j]))))
          
        l.append(sum(squaresum))

    minindex = l.index(min(l))
    sf = list(shift_factor)[minindex]
    nx = x + sf
    nyy2 = []
    for i in range(len(yy2)): 
        ny2 = spl(nx, yy2[i])
        nyy2.append(ny2(x))
   
    return nyy2, sf

nyy2, sf = shift(yy1, yy2)

peaks = [peak(nyy2[i]) for i in range(len(nyy2))]

x3 = [x[i] for i in range(1,len(x)-1)]

def bandwidth(peak_index, region, nyy2):
    
    bandwidth = np.linspace(-5,5,1001)
    p = []
    
    for k in bandwidth:
        l2 = []
        ny2 = []
        
        for i in range(len(peak_index)): 
            lo = peak_index[i][0]-region
            hi = peak_index[i][-1]+region
            l = []
            ny1 = []

            for j in range(lo, hi): 
                l.append(-nyy2[i][j-1]*k + (1+2*k)*nyy2[i][j] - nyy2[i][j+1]*k)
                ny1.append(yy1[i][j])
            
            l2.append(l)
            ny2.append(ny1)            
        
        sumsquare = [sum(abs(sq(l2[i])-sq(ny2[i]))) for i in range(len(peak_index))]
        p.append(sum(sumsquare))

    bw = list(bandwidth)[p.index(min(p))]
    bwy2 = []
    for i in range(len(peak_index)):
        temp = []
        for j in range(1, len(x)-1):
            temp.append(-nyy2[i][j-1]*bw + (1+2*bw)*nyy2[i][j] - nyy2[i][j+1]*bw)
        bwy2.append(temp)
        
    return bwy2, bw

bwy2, bw = bandwidth(peaks, 10, nyy2)

%matplotlib qt
# plt.plot(x, yy1[1], x, nyy2[1], 'g-', x, yy2[1], 'k-')
# plt.plot(x, yy1[2], x, nyy2[2], 'r-', x, yy2[2], 'k-')
# plt.plot(x, yy1[0], x, nyy2[0], 'y-', x, yy2[0], 'k-')
# plt.plot(x3, bwy2[0], 'g-', x, yy1[0], 'b-', x, yy2[0], 'k-')
# plt.plot(x3, bwy2[1], 'g-', x, yy1[1], 'b-', x, yy2[1], 'k-')
# plt.plot(x3, bwy2[2], 'g-', x, yy1[2], 'b-', x, yy2[2], 'k-')
# plt.show()

def calibrate(sf, bw): 
    input_row = int(input('What sample do you want to calibrate?'))
    row = fill_list(sheet2, input_row, 7)
    fn = spl(first_x2, row)
    nx = [num + sf for num in x]
    y = fn(nx)
    
    ny = []
    for i in range(1, len(x)-1):
        ny.append(-y[i-1]*bw + (1+2*bw)*y[i] - y[i+1]*bw)
    
    row1 = fill_list(sheet1, input_row, 7)
    fn1 = spl(first_x, row1)
    y1 = fn1(x) 
    
    x2 = [first_x2[i] for i in range(50,85)]
    y2 = fn(x2)
    %matplotlib qt
    
    plt.plot(x3, ny, 'g-', x, y1, 'b-', x2, y2, 'r--')
    plt.show()
    
    return ny

calibrate(sf, bw)
sf, bw