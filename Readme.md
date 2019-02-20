# Overview 

The Calibration Transfer Algorithm (CTA) optimizes the parameters used for fitting the response profile of a “secondary” spectrometer to the profile of the “master” instrument. The CTA uses functions of interpolation, differentiation and integration, horizontal shifting, and bandwidth. The parameter optimization uses the least sum of differences model.

# Procedure

The algorithm starts by importing all relevant and necessary modules. Modules are explained in detail in the next section. The user is prompted to select the file path of both the master and secondary instruments. The master instrument is assumed by the program to be the first file.
The algorithm also assumes that the files are in the same format as they are after being exported from the spectrometer web application. However, it can easily accommodate a change in format. The program reads the absorbance sheets of both excel files and scrapes the first row, the x values, and any specified rows thereafter (where each subsequent row corresponds to the y-values of a particular sample). Finally, the algorithm sends the data through several functions (explained in the functions section), looking for the optimal parameters, before outputting the plots of the calibration samples as well as the bandwidth and shifting parameters. The default interpolation range is from ~500-650 (this is not an exact range due to small differences in the wavelength ranges of the spectrometers), but can be modified to suit the range of the sample. Functionality exists to give the algorithm a validation set whereby its response profile is corrected based on the return values of the bandwidth and shifting functions. Currently, this function is turned off.


# Modules
	Tkinter: Is a GUI package which is used to prompt the user for the excel files
	Openpyxl: Is a library which facilitates the reading and writing of excel documents
	Matplotlib: Is a plotting library. The CTA uses its pyplot module to plot the calibration results and compare it to original data.
	SciPy: Is a library for numerical routines. The CTA uses: 
  o	Savitzky-Golay filter for first-order differentiation using a window-length of 7 and cubic polynomial 
  o	Interpolated Univariate Spline for interpolation with its default parameters
  o	Cumulative Trapezoidal rule for integration with its default parameters
	NumPy: Is a module for scientific computing. The CTA uses its mathematical expressions.
	Peakutils: Is a module for detecting peaks in 1D graphs. The peakutils.indexes method is used to narrow down the range for the bandwidth function.

# Functions 

*Interpolation*
The CTA uses the Interpolated Univariate Spline for interpolation, as explained above. The default parameters of the univariate spline fit a cubic function passing through each point in the set. A function is made for each sample, and then all of them are mapped onto the master instrument’s set of x-values. This way, the least sum of differences can be calculated.

*Differentiation and Integration*
As with the interpolation function above, differentiation and integration are performed using external python modules. Namely, the scipy.signal.sav_gol method and the scipy.integrate.cumtrapz method. The Savitzky Golay filter is used to smooth data and can be used to find the derivative of a function. The CTA smooths over 7 points, and uses a cubic spline interpolation. The cumulative trapezoidal method approximates a definite integral by taking the sum of areas of trapezoids with a width of 1.

*Horizontal Shift*
The purpose of the shift function is to correct for differences in the placement of the photodiode array. The inter instrument agreement (IIA) is a tolerance value for how two instruments read the same colour. The IIA for the Raspberry spegg VIS22 spectrometer, the device used at the time of this documentation, is 0.5 nm. Therefore, the return value of the shift function should be less than 1 nm (± 0.5 nm) for a reasonable instrument.
The shift function requires two parameters, two N by M arrays (they must have the same shape). Where N is the y-values within the interpolation range, and M is the number of samples to be calibrated.
A ‘shift_factor’ array is initialized to iterate over 1001 values between -5 and 5. Then, a new x data set shifted by the incrementing values in ‘shift_factor’, is created in a for loop. Then a nested for loop interpolates the y-values of each sample from the secondary instrument with this new x data set; the interpolation will return a function. This function is then operated on by the original x data set of the master instrument. If these y values are plotted, they would be shifted by a value of shift_factor. The y-values of the master instrument and the shifted y-values of the secondary instrument are subtracted, and the sum of the absolute value of this new array is appended to a list called ‘squaresum’ which indexes the error associated with each shift factor. This process is repeated for each sample. The value of shift_factor that yields the smallest error is returned and is returned by the function along with the shifted y-values of the secondary instrument.

*Bandwidth*
The purpose of the bandwidth function is to correct for differences in spectral bandwidth. Optimal bandwidth is quoted to be 1/10th the width of the absorbance peak at half maximum, or 1/10th of the FWHM. For example, the best signal-to-noise ratio (SNR) for a sample that has a 40 nm FWHM will be produced with a spectral bandwidth around 4 nm. Thus, deviations in a spectrometer’s spectral bandwidth will be expressed in their response curves. A device with a higher SNR will produce a more exaggerated curve, with higher peaks and lower troughs. The bandwidth function artificially changes the effective bandwidth of the secondary instrument to look more like the master instrument.

The function uses the following relationship: - Y-1¬ * k + (1+2k) * Y0 - Y+1 * k. Where
  -	k is the bandwidth coefficient. A positive value exaggerates the curve while a negative k will compress a curve. When k = 0, the curve is unchanged.
  -	Y-1, Y0, and Y+1 are three consecutive y-values. The expression is a linear combination of these values
  
The bandwidth function requires four parameters, an array of peak indices, the region of bandwidth calculation, the shifted y-values of the secondary instrument, and the original y-values of the master instrument.
The peak index parameter is calculated beforehand. The peakutils.indexes method finds peaks in the plots and stores their indices in a list. These indices are then used to determine the region of bandwidth calculation.
First, a bandwidth array is initialized with 1001 values between -5 and 5. An empty list, p, is used to index the error associated with each bandwidth value. The first ‘for’ loop is used to iterate through the bandwidth values, this namespace contains empty lists, l2 and ny2, which are to contain the new y-values of the secondary and master instrument, respectively. The reason why the master instrument’s y values need to be modified is because the working range of the bandwidth function will vary. To calculate error, both arrays must be the same length. The first nested loop defines the range of calculation for a particular sample. Note that each sample may have different ranges depending on the location of the peaks. The second nested loop applies the bandwidth filter on the secondary instrument and appends it to list, l. Master instrument y-values are appended to the ny1 list. 
The ‘sumsquare’ list contains M values for each iteration. Each member of ‘sumsquare’ is the error of sample m, at bandwidth k. The sum of this list represents the total error at bandwidth k and is appended to p. Finally, the minimum value of p is referenced with the bandwidth array to identify the value of k that produces the smallest error. 
The bandwidth function returns the new y-values of the secondary instrument, the k value, and the sum of differences error.

*Calibration (Default: Off)*
The purpose of the CTA is to calibrate the response profile of the secondary instrument with an appropriate number of samples; the algorithm will return a suitable shift factor and bandwidth coefficient to be applied to future samples.
The calibration function takes two parameters, the shift factor and the k value. The function prompts the user to input the row of the sample they want to calibrate. 
The y-values of this sample are interpolated and mapped onto the master instrument’s x-values shifted by the appropriate shift factor, and run through the bandwidth filter. The output data is then plotted against the original y-values and the y-values of the sample from the master instrument.
The new set of y-values is returned.

# Plotting
Plots are generated using matplotlib.pyplot in a new interactive window (pyqt5). Three graphs are provided for each sample: the master instrument, the original secondary instrument, and the adjusted secondary instrument.
