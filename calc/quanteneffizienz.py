import numpy as np
import pandas as pd
import math
import scipy as sci
import scipy.stats 
import scipy.optimize
import matplotlib.pyplot as plt
import re
import os
import sys
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

plotsize_x = 9
plotsize_y = 1/1.667 * plotsize_x # golden ratio for good looking graphs

def Extract_data_from_file(filename, buzzword, sep = " "):
    wls = []
    nums = []
    errs = []
    with open(filename, "r") as filee:
        lines = filee.readlines()

    for line in lines:
        if re.search(buzzword, line):
            lineindex  = lines.index(line)
            break

    def line_is_a_data_line(line):
        lineindexvalid = lines.index(line) > lineindex
        if(lineindexvalid) and line:
            return True
        else:
            return False


    filteredlines = filter(line_is_a_data_line, lines)
    
    for uncleaned in filteredlines:
        vals = []
        for value in uncleaned.split(sep):
            num_or_string = value.strip()
            vals.append(num_or_string)

        if vals[0] and vals[1]:
            wls.append(float(vals[0]))
            nums.append(float(vals[1]))
            if len(vals) > 2:
                errs.append(float(vals[2]))
        
    return np.array(((wls), (nums), (errs)))


def plot_Graph(x_arry, y_arry, filename, dot_label, y_label, x_label, y_errs = None, x_errs = 0):
    figure = plt.figure()
    figure.set_size_inches(plotsize_x,plotsize_y)
    axis = figure.add_subplot(111)
    minorLocator1 = AutoMinorLocator()
    minorLocator2 = AutoMinorLocator()

    axis.yaxis.set_minor_locator(minorLocator1)
    axis.xaxis.set_minor_locator(minorLocator2)
    if(y_errs is None):
        axis.plot(x_arry, y_arry , 'k.', label = dot_label)
    else:
        axis.errorbar(x_arry, y_arry, xerr = x_errs, yerr =  y_errs, fmt = 'k.', label = dot_label)
    axis.legend(loc="best")
    axis.yaxis.grid(True, which='minor')
    axis.yaxis.grid(True, which='major') 
    axis.xaxis.grid(True, which='minor')
    axis.xaxis.grid(True, which='major')    
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    figure.savefig(filename, bbox_inches='tight')

def Integrate_over_sun_specre(quantum_efficiency):
    # delta lambda is 20 nanometers, one has to integrate over lambda
    h = 6.62607004E-34
    c = 299792458.0
    hc = h * c
    # Useful values only come out
    # if i assume that the spectral power density already
    # has the calculation of the width of the polygons in it
    dlamb = 20 * 1.0E-9 # 20 nanometer wide polygon, THIS VALUE IS NOT USED
    spectral_dens = np.array(Extract_data_from_file("../measurements/Sonne20.txt","wavelength"))
    # Watt per cm **2
    Watt_per_cm2 = np.array(spectral_dens[1]) * 1.0E-3 # data was given im mW
    wls = np.array(spectral_dens[0]) * 1.0E-9 # data was given in  nanometers -> now meters
    I = 0.0
    Area_in_cm2 = math.pi * 0.15**2  # radius of the hole = 0.15 cm 
    # Simple polygonal integration
    for i in range( len(wls)-1): # i is index of array
        P = (Watt_per_cm2[i] + Watt_per_cm2[i+1])/2 * Area_in_cm2
        I = I + (P * wls[i]* quantum_efficiency[i])/(hc)
    return I
        
            
def elektronenrate():
# The pyro, csi and asi are datasets, the first
# pyro[0]  contains  the Wavelenghts (as a numpy array), the second,
# pyro[1]  constains the Voltage values (as a numpy array), the third, 
# pyro[2]  contains  relative errors in percent (as a numpy array)
# The same counts for asi and csi arrays
    pyro = np.array(Extract_data_from_file("../measurements/photonrate.dat", "Start:", ","))
    asi = np.array(Extract_data_from_file("../measurements/elektronenrate_aSi.dat","Start:", ","))
    csi = np.array(Extract_data_from_file("../measurements/elektronenrate_cSi.dat", "Start:", ","))

    wls = csi[0] # Wavelenghts

# Quantum - efficiency. The multiplication of
# numpy - arrays is element -wise, so
# np.array([2, 4, 8]) * np.array([1,6,5]) = [2, 24, 40]
# np.arrays can be mutiplied by constants

    qef_csi = list((csi[1])/(pyro[1]*wls))
    csi_err = csi[1]*csi[2]*0.01
    pyro_err = pyro[1]*pyro[2]*0.01
    qef_csi_err = np.sqrt(((csi_err/(pyro[1]*wls))**2 + ((csi[1])*pyro_err/(pyro[1]**2*wls)))**2)
    plateau_begin_index = list(csi[0]).index(950.0) 
    plateau_end_index = list(csi[0]).index(1030.0)
    level_90_percent = np.average(qef_csi[plateau_end_index:plateau_begin_index])

    qef_asi = list((asi[1])/(pyro[1]*wls*level_90_percent))
    asi_err = asi[1]*asi[2]*0.01
    qef_asi_err = np.sqrt(((asi_err/(pyro[1]*wls*level_90_percent))**2 + ((asi[1])*pyro_err/(pyro[1]**2*wls*level_90_percent)))**2)
    
    plot_Graph(asi[0], asi[1], "../bilder/Spannungen_aSi.jpeg","aSi", "Measured Voltage", "wavelengh in nm", y_errs = asi[1] * asi[2] * 0.01)
    plot_Graph(csi[0], csi[1], "../bilder/Spannungen_cSi.jpeg","cSi", "Measured Voltage", "wavelengh in nm")
    plot_Graph(csi[0], qef_csi/level_90_percent, "../bilder/Quanteneffizienz_csi.jpeg","crystalline silicon", "quantum-efficiency", "wavelengh in nm", y_errs = qef_csi_err/level_90_percent)
    plot_Graph(asi[0], qef_asi, "../bilder/Quanteneffizienz_asi.jpeg","amorphous silicon", "quantum-efficiency", "wavelengh in nm", y_errs = qef_asi_err)
    plot_Graph(pyro[0], pyro[1], "../bilder/photonenrate.jpeg","Pyrodetector voltage","Measured pyrodetector voltage" , "wavelengh in nm", y_errs = pyro[1]*pyro[2] * 0.01)
    coulomb = 6.2415E+18
    I_csi = Integrate_over_sun_specre(qef_csi)/coulomb
    I_asi = Integrate_over_sun_specre(qef_asi)/coulomb

    sun_spectral_dens = np.array(Extract_data_from_file("../measurements/Sonne20.txt","wavelength"))
    plot_Graph(sun_spectral_dens[0], sun_spectral_dens[1], "../bilder/Sonnenspektrum.jpeg", "Sonnenspektrum", r"$\frac{mW}{cm^2} \cdot 20nm$", "wavelength in nm")

    print("I_csi: " + str(I_csi))
    print("I_asi: " + str(I_asi))

def main():
    if not os.path.isdir("../bilder"):
        os.mkdir("../bilder")
    elektronenrate()
    
if __name__ == "__main__":
    main()
