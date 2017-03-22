import numpy as np
import pandas as pd
import math
import scipy as sci
import scipy.stats 
import scipy.optimize
import matplotlib.pyplot as plt
import re
import sys
from matplotlib.ticker import AutoMinorLocator
import matplotlib.patches as patches
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
            "Material":"rough crystalline silicon",
            "FileName":"CSIROUGH.DAT",
        },        
        {
            "Material":"flat crystalline silicon",
            "FileName":"CSIFLAT.DAT",
        },                    
]

lighted_graphs = [
    {
        "Material":"amorphous silicon with light",
        "FileName":"aSi_hell",
        "zero_index":131,
        "p_diff":3,
        "m_diff":1,
    },
    {
        "Material":"crystalline silicon with light",
        "FileName":"cSi_hell",
        "zero_index":100,
        "p_diff":2,
        "m_diff":2,
    },
]

dark_graphs = [
    {
        "Material":"amorphous silicon without light",
        "FileName":"aSi_dunkel",
        "zero_index":50,
        "p_diff":2,
        "m_diff":2,
    },
    {
        "Material":"crystalline silicon without light",
        "FileName":"cSi_dunkel",
        "zero_index":50,
        "p_diff":2,
        "m_diff":2,
    },

]

ref_file = file

def append_latex_picure_to_file(openedfile, picturefilename, caption, reference):
    string = """\\begin{figure}[h]
\t\\centering
\t\\includegraphics[width=0.8\\textwidth]{"""+ picturefilename+ """}
\t\\caption{"""+caption+"""}
\t\\label{"""+reference+"""}
\\end{figure}\n\n"""
    openedfile.write(string)




def Extract_data_from_file(filename, buzzword, sep = " "):
    wls = []
    nums = []
    errs = []
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
    
    for uncleaned in filteredlines:
        vals = []
        for value in uncleaned.split(sep):
            num_or_string = value.strip()
            vals.append(num_or_string)

        if vals[0] and vals[1]:
            wls.append(float(vals[0]))
            nums.append(float(vals[1]))
            if vals[2]:
                errs.append(float(vals[2]))
        
    
    
    return (list(wls), list(nums), list(errs))


def plot_Graph(x_arry, y_arry, filename, dot_label, y_label, x_label, y_errs = False, x_errs = 0):
    figure = plt.figure()
    figure.set_size_inches(plotsize_x,plotsize_y)
    axis = figure.add_subplot(111)
    minorLocator1 = AutoMinorLocator()
    minorLocator2 = AutoMinorLocator()

    axis.yaxis.set_minor_locator(minorLocator1)
    axis.xaxis.set_minor_locator(minorLocator2)
    if(y_errs.any()):
        axis.errorbar(x_arry, y_arry, xerr = x_errs, yerr =  y_errs, fmt = 'b^', label = dot_label)
    else:
        axis.plot(x_arry, y_arry , 'b.', label = dot_label)
    axis.legend(loc="best")
    axis.yaxis.grid(True, which='minor')
#    axis.yaxis.grid(True, which='') 
    axis.xaxis.grid(True, which='minor')
#    axis.xaxis.grid(True, which='major')    
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
    (wavelengths, reflections, trash) = Extract_data_from_file(csi["FileName"], "\#DATA")
    #Using refractive index of air = 1
    n_of_R = lambda R : (math.sqrt(R) + 1)/(math.sqrt(R) - 1)
    refr_indizes = map(n_of_R, reflections)
    plot_Graph(wavelengths, refr_indizes, "../bilder/refr_index.jpeg","Refractive Index of crystalline silicon", r"Refractive Index", r"$\lambda$ in nm")
    return dict(zip(wavelengths, refr_indizes))

def Calculate_thickness_amorph_sil(refr_indizes_of_sil, min_wls):
    if(len(min_wavelenghts) != len(refr_indizes_of_sil)):
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
    for pl in lighted_graphs:
        zero_index = pl["zero_index"]
        p_diff = pl["p_diff"]
        m_diff = pl["m_diff"]
        (voltage, current, trash) = Extract_data_from_file(pl["FileName"], "Delay: 1.0ms")
        scaled_curr = list(np.array(current) * 1000)
        picturename  = "../bilder/"+pl["FileName"].split(".")[0]+".jpeg" 

        fit_volts = voltage[zero_index-m_diff:zero_index+p_diff]
        fit_curr = scaled_curr[zero_index-m_diff:zero_index+p_diff]
        fit = LinFit(fit_curr, fit_volts)
        line_curs = map(fit.inv, voltage)
        min_measured_curs = min(scaled_curr)
        max_measured_curs = max(scaled_curr)
        max_u = fit.calc(min(line_curs, key = lambda i: abs(i - min_measured_curs)))
        min_u = fit.calc(min(line_curs, key = lambda i: abs(i - max_measured_curs)))
        
        volt_fit_dots = np.linspace(min_u, max_u)
        curr_fit_dots = map(fit.inv, volt_fit_dots)


        U0 = voltage[current.index(min(current, key= lambda i:abs(i)))] 
        I0 = scaled_curr[voltage.index(min(voltage, key= lambda i:abs(i)))]
        def filter(ui):
            u = ui[0]
            i = ui[1]
            if(i > 0):
                return 0
            if(u < 0):
                return 0
            return u * i
        
        powerlist = map(filter, zip(voltage, current))
        optindex = powerlist.index(min(powerlist))
        Uopt = voltage[optindex]
        Iopt = scaled_curr[optindex]

        FF = (Uopt*Iopt)/(U0 * I0)
        fitlabel = r"Fit for $R_s = \frac{\partial U}{\partial I} |_{I = 0}$"
        figure = plt.figure()
        figure.set_size_inches(plotsize_x,plotsize_y)
        axis = figure.add_subplot(111)
        minorLocator1 = AutoMinorLocator()
        minorLocator2 = AutoMinorLocator()
        axis.plot(voltage, scaled_curr, 'k.', label = pl["Material"])
        axis.plot(volt_fit_dots, curr_fit_dots, 'r--', label = fitlabel)
        axis.add_patch(
            patches.Rectangle(
                (0.0, 0.0),
                U0,
                I0,
                edgecolor = "red",
                alpha = 0.2,
                hatch = '\\'
            ))
        axis.add_patch(
            patches.Rectangle(
                (0.0, 0.0),
                Uopt,
                Iopt,
                edgecolor = "red",
                alpha = 0.4,
                hatch = '/'
            ))
        axis.yaxis.set_minor_locator(minorLocator1)
        axis.xaxis.set_minor_locator(minorLocator2)
        axis.legend(loc="best")
        axis.yaxis.grid(True, which='major')    
        axis.xaxis.grid(True, which='major')
        plt.ylabel("current in mA")
        plt.xlabel("Voltage in V")
        figure.savefig(picturename, bbox_inches='tight')

        print(pl["FileName"]+" R_s:\n" + str(fit))
        print("Fuellfakt: " + str(FF))
        print("U0: " + str(U0))
        print("I0: " + str(I0))
        print("Uopt: " + str(Uopt))
        print("Iopt: " + str(Iopt))
        print("")

        append_latex_picure_to_file(ref_file, picturename[3:], pl["Material"], "fig:"+pl["FileName"].split(".")[0].lower())


    for pl in dark_graphs:
        zero_index = pl["zero_index"]
        p_diff = pl["p_diff"]
        m_diff = pl["m_diff"]
        (voltage, current) = Extract_data_from_file(pl["FileName"], "Delay: 1.0ms")
        scaled_curr = np.array(current) * 1000
        picturename  = "../bilder/"+pl["FileName"].split(".")[0]+".jpeg" 
        
        fit_volts = voltage[zero_index-m_diff:zero_index+p_diff]
        fit_curr = scaled_curr[zero_index-m_diff:zero_index+p_diff]
        fit = LinFit(fit_curr, fit_volts)
        volt_fit_dots = np.linspace(min(voltage),max(voltage))
        inv = lambda u: (u - fit.y_axis)/fit.slope
        curr_fit_dots = map(inv, volt_fit_dots)

        print(pl["FileName"]+" R_p:\n" + str(fit))
        fitlabel = r"Fit for $R_p = \frac{\partial U}{\partial I} |_{U = 0}$"
        figure = plt.figure()
        figure.set_size_inches(plotsize_x,plotsize_y)
        axis = figure.add_subplot(111)
        minorLocator1 = AutoMinorLocator()
        minorLocator2 = AutoMinorLocator()
        axis.plot(voltage, scaled_curr, 'k.', label = pl["Material"])
        axis.plot(volt_fit_dots, curr_fit_dots, 'r-', label = fitlabel)
        axis.yaxis.set_minor_locator(minorLocator1)
        axis.xaxis.set_minor_locator(minorLocator2)
        axis.legend(loc="best")
        axis.yaxis.grid(True, which='major')    
        axis.xaxis.grid(True, which='major')
        plt.ylabel("current in mA")
        plt.xlabel("Voltage in V")
        figure.savefig(picturename, bbox_inches='tight')
        append_latex_picure_to_file(ref_file, picturename[3:], pl["Material"], "fig:"+pl["FileName"].split(".")[0].lower())

def pr_v(name, val, err):
    print(name + ": " + str(val) + " +- " + str(err))

def print_powers(silicon, Popt, dPopt, EFF, dEFF):
    print(silicon)
    pr_v("Popt", Popt * 1000, dPopt * 1000)
    pr_v("EFF", EFF , dEFF)
    
def power():
    dU = 0.005
    dI = 0.005 * 10**(-3)
    # A = Flaeche
    # PL = Incoming Power of Light
    # PPCS = power per centimeter**2
    PPCS = 0.1
    dPPCS = 0.02
    A = math.pi * 0.15**2
    PL = A * PPCS
    dPL = A * dPPCS
    
    U = 0.65
    I = 0.334973 * 10**(-3)

    Popt = U * I 
    dPopt = math.sqrt(U*dI**2 + I*dU**2)

    EFF = Popt/PL
    dEFF = math.sqrt((dPopt/PL)**2 + (Popt*dPL/(PL**2))**2)
    print_powers("Amorph Sil:", Popt, dPopt, EFF, dEFF)
    
    U = 0.38
    I = 2.886767 * 10**(-3)
    Popt = U * I
    dPopt = math.sqrt(U*dI**2 + I*dU**2)

    EFF = Popt/PL
    dEFF = math.sqrt((dPopt/PL)**2 + (Popt*dPL/(PL**2))**2)
    print_powers("Crystalline Sil:", Popt, dPopt, EFF, dEFF)

        
def main():
    ref_file = open("../kapitel/piture_references.txt","w")
    # plot_reflection_graphs()
    # refractive_indizes_info()
    # plot_voltage_graph()
    # power()
    ref_file.close()

    
if __name__ == "__main__":
    main()
