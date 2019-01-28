from scipy.interpolate import InterpolatedUnivariateSpline as spl
import time

# Saving a 1D array of the x-values of each instrument
first_x = fill_list(sheet1, 1, 7)
first_x2 = fill_list(sheet2, 1, 7)

# saving a 1D array of the first set of y-values of each instrument (should correspond to the same sample)
first_row = fill_list(sheet1, 2, 7)
first_row2 = fill_list(sheet2, 2, 7)

x = np.linspace(500,650,251)

#interpolation: we can know all y-values between 450 and 700 nm. 
y1 = spl(first_x, first_row) # function
y2 = spl(first_x2, first_row2) # function

# interpolated y-values
yy1 = y1(x)
yy2 = y2(x)

def shift():
    l = [] # array of the sum of squares
    
    shift_factor = np.linspace(-3, 3, 61)
    
    # Let's choose y1 as our master instrument
    # we need to shift y2 so that it has the smallest sum of squares with y1
    for i in shift_factor:
        nx = x + i
        ny2 = spl(nx, yy2) # same shape
        nyy2 = ny2(x) # new y-values
        l.append(sum(sq(yy1)-sq(nyy2)))
    
    minum = [abs(num) for num in l]
    minindex = minum.index(min(minum))
    sf = list(shift_factor)[minindex]
    nx = x + sf
    ny2 = spl(nx, yy2)
    nyy2 = ny2(x)
    return yy1, nyy2, sf

y1, y2, sf= shift()

bwtest = filedialog.askopenfilenames(filetype = [("Excel File","*.xlsx")])
wb = load_workbook(str(bwtest[0]))
wsheet = wb['Sheet1']
yes = fill_list(wsheet, 2, 2)

k = -0.5;
l = []
for i in range(1, 200): 
    l.append(-1* yes[i-1]*k + (1+2*k)*yes[i] -1*yes[i+1]*k)

x3 = np.linspace(450,649, 199)

plt.plot(x3, l)

# def bandwidth(): 
    
#     # pick y1 as master. Bandwidth shift to y2.
#     blah = np.linspace(-2,2,101)
#     p = []
#     for k in blah:
#         l = []
#         ny1 = []

#         for i in range(1, len(y2)-1): 
#             l.append(-y2[i-1]*k + (1+2*k)*y2[i] - y2[i+1]*k)
#             ny1.append(y1[i])

#         p.append(sum(sq(l)-sq(ny1)))

#     minum = [abs(num) for num in p]
#     bw = -5
#     ny2 = []
#     print(bw)
#     for i in range(1, len(y2)-1): 
#         ny2.append(-y2[i-1]*bw + (1+2*bw)*y2[i] - y2[i+1]*bw)
#     return ny2
        
# y3 = bandwidth()
# plt.figure(figsize=[30,30])
# x2 = np.linspace(501,650,249)
# plt.plot(x, y2, x2, y3, 'g-', x, yy1, 'r-')
# plt.ylim(1,1.7)
# plt.xlim(500,600)