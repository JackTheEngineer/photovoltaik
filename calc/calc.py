import numpy as np
import pandas
import math
import scipy as sci
import scipy.stats 
import scipy.optimize
import matplotlib.pyplot as plt
import re
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from Measurement import LinFit

plotsize_x = 9
plotsize_y = 1/1.667 * plotsize_x # golden ratio for good looking graphs


def Extract_data_from_file(filename):
    wls = []
    nums = []
    with open("../measurements/"+filename, "r") as filee:
        lines = filee.readlines()

    for line in lines:
        if re.search(r"\s*\#DATA\s*", line):
            lineindex  = lines.index(line)
            break

    def line_is_a_data_line(line):
        lineindexvalid = lines.index(line) > lineindex
        if(lineindexvalid) and line:
            return True
        else:
            return False


    filteredlines = filter(line_is_a_data_line, lines)
    
    for value in filteredlines:
        vals = value.split()
        wls.append(float(vals[0]))
        nums.append(float(vals[1]))

    return (wls, nums)
        


def main():

    FileNames = [
        {
            "Material":"silicon mit pyramidal surface",
            "FileName":"PyramidSilizium.DAT",
        },
        {
            "Material":"black silicon",
            "FileName":"BlackSilizium.DAT",
        },
        {
            "Material":"silicon with antireflective coating",
            "FileName":"AntiReflectiveCoating.DAT",
        },
        {
            "Material":"amorphous silicon",
            "FileName":"AmorphSilizium.DAT",
        },
        {
            "Material":"flat crystalline silicon",
            "FileName":"CSIROUGH.DAT",
        },        
        {
            "Material":"rough crystalline silicon",
            "FileName":"CSIFLAT.DAT",
        },                    
        ]

    for pl in FileNames:

        (wals, reflections) = Extract_data_from_file(pl["FileName"])
                
        # Plot plot with two fits  
        figure = plt.figure()
        figure.set_size_inches(plotsize_x,plotsize_y)
        axis = figure.add_subplot(111)
#        plt.xlim(200, 20)
        minorLocator1 = AutoMinorLocator()
        minorLocator2 = AutoMinorLocator()
        axis.plot(wals, reflections , 'b.', label = pl["Material"])
        axis.yaxis.set_minor_locator(minorLocator1)
        axis.xaxis.set_minor_locator(minorLocator2)
#        axis.errorbar(concentrations, speeds, xerr = concentrations * 0.05, yerr =  speed_errors, fmt = 'b^', label = "Konzentration in mmol")
        axis.legend(loc="best")
        axis.yaxis.grid(True, which='major')    
        axis.xaxis.grid(True, which='major')    
        plt.xlabel(r"$\lambda$ in nm")
        plt.ylabel(r"reflectivity in %")
        figure.savefig("../bilder/"+pl["FileName"].split(".")[0]+".jpeg", bbox_inches='tight')
    
if __name__ == "__main__":
    main()
