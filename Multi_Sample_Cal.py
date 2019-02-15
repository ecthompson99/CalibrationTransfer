#Importing modules

import tkinter as tk
from tkinter import filedialog
from openpyxl import load_workbook
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline as spl
import numpy as np
from numpy import square as sq
from peakutils import indexes as peak

root = tk.Tk()
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

# picking the interval of rows of calibration samples
rcal_i = [i for i in range(28,34)] # for shift

first_x = fill_list(sheet1, 1, 7) 
first_x2 = fill_list(sheet2, 1, 7) 

first_row = [] # stores the sets of y-values for the calibration samples of the main instrument
first_row2 = [] # stores the sets of y-values for the calibration samples of the secondary instrument

y1 = []
y2 = []
yy1 = []
yy2 = []

x = [first_x[i] for i in range(40, 100)] # Here, the range of y-values are chosen

for i in rcal_i:
    first_row.append(fill_list(sheet1, i, 7))
    first_row2.append(fill_list(sheet2, i, 7))

for i in range(len(rcal_i)):
    y1.append(spl(first_x, first_row[i]))
    y2.append(spl(first_x2, first_row2[i]))
    yy1.append(y1[i](x))
    yy2.append(y2[i](x))

# -------------------- FUNCTIONS -----------------------------------

# Mean subtraction

mean_yy1 = [np.mean(yy1[i]) for i in range(len(yy1))]
mean_yy2 = [np.mean(yy2[i]) for i in range(len(yy2))]
   
sm_yy1 = []
sm_yy2 = []
for i in range(len(yy1)): 
    sm_yy1.append([yy1[i][j] - mean_yy1[i] for j in range(len(yy1[i]))])
    sm_yy2.append([yy2[i][j] - mean_yy2[i] for j in range(len(yy1[i]))])

# shifting function

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
            
            squaresum.append(sum(abs(yy1[j]-nyy2[j])))
          
        l.append(sum(squaresum))

    minindex = l.index(min(l))
    sf = list(shift_factor)[minindex]
    nx = x + sf
    nyy2 = []
    for i in range(len(yy2)): 
        ny2 = spl(nx, yy2[i])
        nyy2.append(ny2(x))
   
    return nyy2, sf

nyy2, sf = shift(sm_yy1, sm_yy2)


# Bandwidth Function
peaks = [peak(nyy2[i]) for i in range(len(nyy2))]

x3 = [x[i] for i in range(1,len(x)-1)]

def bandwidth(peak_index, region, nyy2, yy1):
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
        
        sub_arrays = [[abs(a - b) for (a, b) in zip(l2[i], ny2[i])] for i in range(len(peak_index))]
        sumsquare = [sum(num) for num in sub_arrays]
        p.append(sum(sumsquare))

    bw = list(bandwidth)[p.index(min(p))]
    bwy2 = []
    for i in range(len(peak_index)):
        temp = []
        for j in range(1, len(x)-1):
            temp.append(-nyy2[i][j-1]*bw + (1+2*bw)*nyy2[i][j] - nyy2[i][j+1]*bw)
        bwy2.append(temp)
        
    return bwy2, bw, min(p)

bwy2, bw, err = bandwidth(peaks, 5, nyy2, sm_yy1)

# # calculating the error involved
# yyy1 = []
# sumsquare = []
# for i in range(len(bwy2)):
#     yyy1.append(y1[i](x3))
#     sumsquare.append(sum(abs(bwy2[i]-yyy1[i])))
    
def calibrate(sf, bw): 
    input_row = range(28, 34)

    # new y2 data
    row = [fill_list(sheet2, input_row[i], 7) for i in range(len(input_row))]
    fn = [spl(first_x2, row[i]) for i in range(len(input_row))]
    nx = [num + sf for num in x]
    oy = [fn[i](nx) for i in range(len(fn))]
    
    # original mean-centered y1 data
    row1 = [fill_list(sheet1, input_row[i], 7) for i in range(len(input_row))]
    fn1 = [spl(first_x, row1[i]) for i in range(len(input_row))]
    oy1 = [fn1[i](nx) for i in range(len(fn1))]
    
    # old y2 data
    x2 = [first_x2[i] for i in range(40,100)]
    oy2 = [fn[i](x2) for i in range(len(fn))]
    
    # calculating the mean-centered plots
    mean0 = [np.mean(oy[i]) for i in range(len(oy))]
    mean1 = [np.mean(oy1[i]) for i in range(len(oy1))]
    mean2 = [np.mean(oy2[i]) for i in range(len(oy2))]

    for i in range(len(mean0)):
        y = y + [oy[i][j]-mean0[i] for j in range(len(oy[i]))]
        y1 = y1 + [oy1[i][j]-mean1[i] for j in range(len(oy1[i]))]
        y2 = y2 + [oy[i][j]-mean2[i] for j in range(len(oy2[i]))]
    
    ny = []

    for j in range(len(y)):
        for i in range(1, len(x)-1):
            ny.append(-y[j][i-1]*bw + (1+2*bw)*y[j][i] - y[j][i+1]*bw)
    
    plt.figure().text(0.5, .05, "The difference of squares error is: " + str(err), ha='center', va='bottom')
    for i in range(0,1):
        plt.plot(x3, ny[i], 'g-', label="new")
        plt.plot(x, y1[i], 'b-', label="master")
        plt.plot(x2, y2[i], 'r--', label="old")
        plt.legend(loc="best")
        plt.show()
    
    return ny

calibrate(sf, bw)

sf, bw, err
    
# ------------------------- PLOTS --------------------------------------

# %matplotlib qt

# fig = plt.figure()
# fig.text(0.5, .05, "The difference of squares error is: " + str(sum(sumsquare)), ha='center', va='bottom')
# # plt.plot(x, yy1[1], x, nyy2[1], 'g-', x, yy2[1], 'k-')
# # plt.plot(x, yy1[2], x, nyy2[2], 'r-', x, yy2[2], 'k-')
# # plt.plot(x, yy1[0], x, nyy2[0], 'y-', x, yy2[0], 'k-')
# plt.ylim(-0.75,1.25)
# plt.plot(x3, bwy2[0], 'g-', x, sm_yy1[0], 'b-', x, sm_yy2[0], 'r-')
# plt.plot(x3, bwy2[1], 'g-', x, sm_yy1[1], 'b-', x, sm_yy2[1], 'r-')
# plt.plot(x3, bwy2[2], 'g-', x, sm_yy1[2], 'b-', x, sm_yy2[2], 'r-')
# plt.plot(x3, bwy2[3], 'g-', x, sm_yy1[3], 'b-', x, sm_yy2[3], 'r-')
# plt.plot(x3, bwy2[4], 'g-', x, sm_yy1[4], 'b-', x, sm_yy2[4], 'r-')
# plt.plot(x3, bwy2[5], 'g-', x, sm_yy1[5], 'b-', x, sm_yy2[5], 'r-')
# plt.title('Without derivative function')
# plt.show()