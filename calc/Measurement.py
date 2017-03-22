import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from matplotlib.ticker import AutoMinorLocator

class Measurement(object):
    def __init__(self, x_values, y_values, name, x_error = None, y_error = None):
        self.x_values = np.array(x_values)
        self.y_values = np.array(y_values)
        if(x_error == None):
            self.x_error = None
        else:
            self.x_error = np.array(x_error)

        if(y_error == None):
            self.y_error = None
        else:
            self.y_error = np.array(y_error)

        self.name = name
        
    def set_x_error(self, x_error):
        self.x_error = np.array(x_error)

    def set_y_error(self, y_error):
        self.y_error = np.array(y_error)

    def savegraph(self, xlabel, ylabel, markersize = 3, fmt = "ko--"):
        minorLocator = AutoMinorLocator()
        figure = plt.figure()
        figure.set_size_inches(7, 4)
        axis =  figure.add_subplot(111)

        axis.plot(self.x_values, self.y_values, fmt, label = self.name, markersize = markersize)
        
        axis.xaxis.set_minor_locator(minorLocator)
        plt.xlim(min(self.x_values)-0.2, max(self.x_values)+0.2)

        axis.grid()
        axis.xaxis.grid(True, which='minor')
        axis.legend(loc="best")
        plt.xlabel(xlabel) 
        plt.ylabel(ylabel)
        figure.savefig("../bilder/"+self.name, bbox_inches='tight',dpi=100)

def Linfunc(x, m, t):
    return x*m + t

class LinFit(object):
    def __init__(self, x_values, y_values):
        self.x_values = np.array(x_values)
        self.y_values = np.array(y_values)
        self.slope = 0
        self.slope_err = 0
        self.y_axis = 0 
        self.y_axis_error = 0
        self.calculate_Opt()
        
    def __str__(self):   
        string = "Slope: " + str(self.slope) + " +- " + str(self.slope_err) + '\n' + "y_axis: " + str(self.y_axis) + " +- " + str(self.y_axis_error)
        return string
        
    def calculate_Opt(self):
        (popt, pcov) = scipy.optimize.curve_fit(Linfunc, self.x_values, self.y_values)
        (self.slope, self.y_axis) = popt
        (self.slope_err, self.y_axis_error) = np.sqrt(np.diag(pcov))

    def calc(self, x): 
        return float(self.slope) * float(x) + float(self.y_axis)

    def inv(self, y):
        return (float(y) - float(self.y_axis))/float(self.slope)
    
# class colour_max_measurement(object):
    # def __init__(self, name, distance, x_values, y_values):
        # self.x_values = np.array(values)
        # self.y_values = np.array(y_values)
        # self.name = str(name)
        # self.distance = distance
        # self.linfit = None

    # def calculate_fit(self):
        # self.linfit = LinFit()
