from matplotlib import pyplot as plt
import numpy as np
from copy import deepcopy

fig = plt.figure()

x1 = range(0, 50, 1)
y1 = [i**1.5 for i in x1]
y2 = [i*5 for i in x1]
k_y1 = 0.283
k_y2 = 0.00134
y3 = [k_y1*i+k_y2*j for (i, j) in zip(y1,y2)]

# plt.figure(figsize=[10,10])
# plt.plot(x1, y1, 'r-', label="first")
# plt.plot(x1, y2, 'g-', label="second")
# plt.plot(x1, y3, 'b', label="linear combination: {}*first + {}*second".format(k_y1, k_y2))

# plt.legend(loc="best")

indices = [10,40]
# matrix = np.array([[y1[10], y2[10], y3[10]],
#                   [y1[40], y2[40], y3[40]]])

# matrix = np.array(range(36), dtype="float64").reshape(6,6)
matrix = np.array([[1, 2, 3, 9],
                   [2, -1, 1, 8],
                   [3, 0, -1, 3]])

# matrix[0] = [y1[i] for i in indices]
# matrix[1] = [y2[i] for i in indices]

def ref_reduction(matrix): 

    row, col = matrix.shape

    # if not, start gaussian elimination
    for c in range(col-1): 
        
        # is matrix already in REF?
        ref = True

        for i in range(1, row): 
            for j in range(col): 
                wrow = matrix[i+j:, j]
                if sum([np.square(k) for k in wrow]) != 0 or matrix[i-1,j] != 1:
                    ref = False
        if ref:
            return matrix
        
        # make sure first diagonal element of the iteration isn't zero. If so, swap rows with next non-zero element in same row
        j=c

        if matrix[j, c] == 0:
            j +=1
        if j != c: 
            matrix[c,:], matrix[j,:] = deepcopy(matrix[j,:]), deepcopy(matrix[c,:])
            # print("switched row {} with row {}".format(c, j))

        # making diagonal element a leading 1
        first_entry = matrix[c, c]

        matrix[c,:] = [matrix[c,i]/first_entry for i in range(col)]

        for r in range(c+1, row):

            matrix[r, :] = matrix[r,:]-matrix[r,c]*matrix[c,:]
        print(matrix)

    return matrix

def syslin_solve(matrix):
    row, col = matrix.shape()
    matrix = np.fliplr(np.flipud(matrix))
    
    # comparison matrix
#     new_yes = list(np.ravel(yes))
#     matrix1 = [num/num if num != 0 else 0 for num in new_yes]
#     matrix2 = np.asarray(matrix1).reshape(matrix.shape)
    
    coefficients = range(len(row))
    c = matrix[:,0]
    for i in range(row):
        for j in range(1, col):
            if matrix[i,j+1] == 0 : 
                coefficients[i] = c[j-1] / matrix[i,j]
                print(matrix)
                break
            else: 
                c[j-1] -= matrix[i,j]*coefficients[j-1]
            
        
print(np.fliplr(np.flipud(matrix)))
    
    