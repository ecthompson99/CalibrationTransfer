from matplotlib import pyplot as plt
import numpy as np
from copy import deepcopy

# --------- EXAMPLE OF A LINEAR COMBINATION OF TWO CURVES -------------

x1 = range(0, 50, 1)
y1 = [i**1.5 for i in x1]
y2 = [i*5 for i in x1]
k_y1 = 0.283
k_y2 = 0.00134
y3 = [k_y1*i+k_y2*j for (i, j) in zip(y1,y2)]

plt.figure(figsize=[10,10])
plt.plot(x1, y1, 'r-', label="first")
plt.plot(x1, y2, 'g-', label="second")
plt.plot(x1, y3, 'b', label="linear combination: {}*first + {}*second".format(k_y1, k_y2))
plt.legend(loc="best")
plt.show()

y = [y1,y2,y3] # a list of the y-data
indices = [10,40] # indices should be the areas where the relationship is linear. number of indices should be equal to the number of curves

matrix = np.ones([len(indices), len(y)])
for i in range(len(indices)):
    for j in range(len(y)):
        matrix[i,j] = y[j][indices[i]]
        
print(matrix)

# ------------ end of data -----------------------------------------------

# ------------ FUNCTIONS -------------------------------------------------

# method for quickly solving a system of linear equations. Row echelon reduction.

def ref_reduction(matrix): 
    """Takes an N x M matrix and converts it into row-echelon form.
    
    Takes a matrix of any size (with reason), and returns its corresponding row-echelon form.
    Thus, all diagonal elements are one, and all lower triangular elements (below the diagonal) are zero. This applies
    to a linearly independent set of equations. However, systems of equations which are linearly dependent may have different 
    shapes. For instance, in a 6 x 6 matrix only the first two lines may be filled implying that 4 of the rows are linearly
    dependent on the first two. 
    
    """

    row, col = matrix.shape # find the number of rows and columns

    # iterates through all working columns
    for c in range(col-1): 
        
        # is matrix already in REF? If so, return the matrix
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

        # divide all values by the first entry in that row
        matrix[c,:] = [matrix[c,i]/first_entry for i in range(col)]

        # subtract the product of the leading element and the preceding row. this should make the first non-zero element of that row a zero.
        for r in range(c+1, row):

            matrix[r, :] = matrix[r,:]-matrix[r,c]*matrix[c,:]

    return matrix

REF_matrix = ref_reduction(matrix)

def syslin_solve(matrix):
    """ Function which solves matrices in row-echelon form.
    
    Takes a matrix in row-echelon form and returns the coefficients of all variables.
    
    """
    row, col = matrix.shape
    matrix = np.fliplr(np.flipud(matrix))
    coefficients = list(np.ones(row))
    for i in range(row):
        j = 1
        c = matrix[:,0]
        while j < i+1:
            c[i] -= matrix[i,j]*coefficients[j-1]
            j += 1
        coefficients[i] = c[i] / matrix[i,j]
                
    return list(reversed(coefficients))

coefficients = syslin_solve(REF_matrix)
print(coefficients)
