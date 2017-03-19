import numpy as np
import pandas
import math
import scipy as sci
import scipy.stats 
import scipy.optimize
import matplotlib.pyplot as plt
import re
import sys
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from Measurement import LinFit

plotsize_x = 9
plotsize_y = 1/1.667 * plotsize_x # golden ratio for good looking graphs

min_wavelenghts = list([1955.0, 1515.00, 1245.00])
refr_indizes_of_silicon = []

e_charge = 1.602176*10**(-19)

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

VoltageGraphs = [
    {
        "Material":"amorphous silicon with light",
        "FileName":"aSi_hell",
    },
    {
        "Material":"amorphous silicon without light",
        "FileName":"aSi_dunkel",
    },
    {
        "Material":"crystalline silicon with light",
        "FileName":"cSi_hell",
    },
    {
        "Material":"crystalline silicon without light",
        "FileName":"cSi_dunkel",
    },
]

def append_latex_picure_to_file(openedfile, picturefilename, caption, reference):
    string = """\\begin{figure}[h]
\t\\centering
\t\\includegraphics[width=0.8\\textwidth]{"""+ picturefilename+ """}
\t\\caption{"""+caption+"""}
\t\\label{"""+reference+"""}
\\end{figure}\n\n"""
    openedfile.write(string)




def Extract_data_from_file(filename, buzzword):
    wls = []
    nums = []
    with open("../measurements/"+filename, "r") as filee:
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
    
    for value in filteredlines:
        vals = value.split()
        wls.append(float(vals[0]))
        nums.append(float(vals[1]))

    return (list(wls), list(nums))


def plot_Graph(x_arry, y_arry, filename, dot_label, y_label, x_label):
                       # Plot plot with two fits  
        figure = plt.figure()
        figure.set_size_inches(plotsize_x,plotsize_y)
        axis = figure.add_subplot(111)
        minorLocator1 = AutoMinorLocator()
        minorLocator2 = AutoMinorLocator()
        axis.plot(x_arry, y_arry , 'b.', label = dot_label)
        axis.yaxis.set_minor_locator(minorLocator1)
        axis.xaxis.set_minor_locator(minorLocator2)
#        axis.errorbar(concentrations, speeds, xerr = concentrations * 0.05, yerr =  speed_errors, fmt = 'b^', label = "Konzentration in mmol")
        axis.legend(loc="best")
        axis.yaxis.grid(True, which='major')    
        axis.xaxis.grid(True, which='major')    
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        figure.savefig(filename, bbox_inches='tight')

def plot_reflection_graphs():
    ref_file = open("../kapitel/piture_references.txt","w")
    for pl in FileNames:
        (wavelengths, reflections) = Extract_data_from_file(pl["FileName"], "\#DATA")

        picturename  = "../bilder/"+pl["FileName"].split(".")[0]+".jpeg" 
        plot_Graph(wavelengths, reflections, picturename, pl["Material"], r"reflectivity in %", r"$\lambda$ in nm")
        append_latex_picure_to_file(ref_file, picturename[3:], pl["Material"], "fig:"+pl["FileName"].split(".")[0].lower())
    ref_file.close()

        
def plot_refractive_Index():
    csi = FileNames[-1]
    (wavelengths, reflections) = Extract_data_from_file(csi["FileName"], "\#DATA")
    #Using refractive index of air = 1
    n_of_R = lambda R : (math.sqrt(R) + 1)/(math.sqrt(R) - 1)
    refr_indizes = map(n_of_R, reflections)
    plot_Graph(wavelengths, refr_indizes, "../bilder/refr_index.jpeg","Refractive Index of crystalline silicon", r"Refractive Index", r"$\lambda$ in nm")
    return dict(zip(wavelengths, refr_indizes))

def Calculate_thickness_amorph_sil(refr_indizes_of_sil, min_wls):
    if(len(min_wavelenghts) != len(refr_indizes_of_sil)):
        print(min_wavelenghts)
        print(refr_indizes_of_sil)
        sys.exit("ERROR: Lenghts of refractive indizes and minimal wavelenghts arrays were not the same")

    thicknesses = []
    num_of_waves_in_glass = lambda lamb_1, lamb_2: 0.5*(lamb_2/(lambd_1 - lamb_2) -1)
    for i in range(len(min_wavelenghts) -1):
        lambd_1 = min_wls[i]*1/refr_indizes_of_sil[i]
        lambd_2 = min_wls[(i+1)]*1/refr_indizes_of_sil[(i+1)]
        n = num_of_waves_in_glass(lambd_1, lambd_2)
        thicknesses.append((2*n +1)*lambd_1*1/2)

    avg = np.average(np.array(thicknesses))
    dev = np.std(np.array(thicknesses))
    print("average of thicknesses: " + str(avg))
    print("stdev: " + str(dev))

def refractive_indizes_info():
    refr_i = []
    refr_dict = plot_refractive_Index()
    for wl in min_wavelenghts:
        refr_i.append(refr_dict[wl])
    print("Refractive Indizes for wavelenghts: " + str(refr_i))
    print("Wavelenghts: " + str(min_wavelenghts))
    Calculate_thickness_amorph_sil(refr_i, min_wavelenghts)

def plot_voltage_graph():
    zero_index = 50
    diff = 2
    for pl in VoltageGraphs:
        (voltage, current) = Extract_data_from_file(pl["FileName"], "Delay: 1.0ms")
        scaled_curr = np.array(current) * 1000
        picturename  = "../bilder/"+pl["FileName"].split(".")[0]+".jpeg" 
        plot_Graph(voltage, scaled_curr, picturename, pl["Material"], r"Current in mA, with light", r"Voltage in V") 

#         fit_volts = voltage[zero_index-diff:zero_index+diff]
#         fit_curr = scaled_curr[zero_index-diff:zero_index+diff]
#         fit = LinFit(fit_curr, fit_volts)
#         volt_fit_dots = np.linspace(min(voltage),max(voltage))
#         inv = lambda u: (u - fit.y_axis)/fit.slope
#         curr_fit_dots = map(inv, volt_fit_dots)

#         fitlabel = r"fit of $\frac{\partial U}{\partial I}$ at U = 0"
#         figure = plt.figure()
#         figure.set_size_inches(plotsize_x,plotsize_y)
#         axis = figure.add_subplot(111)
#         minorLocator1 = AutoMinorLocator()
#         minorLocator2 = AutoMinorLocator()
#         axis.plot(voltage, scaled_curr, 'b.', label = "current in mA, no light")
#         axis.plot(volt_fit_dots, curr_fit_dots, 'r-', label = fitlabel)
#         axis.yaxis.set_minor_locator(minorLocator1)
#         axis.xaxis.set_minor_locator(minorLocator2)
# #        axis.errorbar(concentrations, speeds, xerr = concentrations * 0.05, yerr =  speed_errors, fmt = 'b^', label = "Konzentration in mmol")
#         axis.legend(loc="best")
#         axis.yaxis.grid(True, which='major')    
#         axis.xaxis.grid(True, which='major')
#         plt.ylabel("current in mA")
#         plt.xlabel("Voltage")
#         figure.savefig(picturename, bbox_inches='tight')

def main():
    #plot_reflection_graphs()
    #refractive_indizes_info()
    plot_voltage_graph()
    

    
if __name__ == "__main__":
    main()
