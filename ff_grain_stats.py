#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
original author: ksg52
"""
"""
produce histograms of stats from grains.out files from ff hedm
written to be called from command line
"""


# %% Imports - NO CHANGES NEEDED
#==============================================================================
# General Imports
import argparse
import numpy as np
#import multiprocessing as mp
import os
import psutil
import copy
from scipy.stats import norm
import copy

# Hexrd imports
import hexrd

# Matplotlib
# This is to allow interactivity of inline plots in your gui
# the import ipywidgets as widgets line is not needed - however, you do need to run a pip install ipywidgets
# the import ipympl line is not needed - however, you do need to run a pip install ipympl
#import ipywidgets as widgets
#import ipympl 
import matplotlib
# The next line is formatted correctly, no matter what your IDE says
#%matplotlib widget
#%matplotlib inline
import matplotlib.pyplot as plt

if __name__ == '__main__':
    #
    #  Run preprocessor
    #
    parser = argparse.ArgumentParser(
        description="produce histograms of statistics from grains.out file")

    parser.add_argument('grains_fpath',
                        help="full path to grains.out file", type=str)
    parser.add_argument('grains_fname',
                        help="grains.out filename", type=str)
    parser.add_argument('var_for_hist',
                        help="variable to histogram e.g. chisq, completeness, ...", type=str)
    parser.add_argument('-o', '--output_fname',
                        help="output filename", type=str, default="")
    parser.add_argument('-n','--xmin',
                        help="x-axis min value", type=float, default="-1")
    parser.add_argument('-x', '--xmax',
                        help="x-axis max value", type=float, default="-1")                    
    args = parser.parse_args()

    # strip args
    grains_fpath = args.grains_fpath
    grains_fname = args.grains_fname
    var_for_hist = args.var_for_hist
    output_fname = args.output_fname
    xmin = args.xmin 
    xmax = args.xmax
    
    #make sure the grains.out file exists
    grains_full_fname = os.path.join(grains_fpath, grains_fname)
    check_files_exist = os.path.exists(grains_full_fname) 
    if not np.all(check_files_exist):
        raise RuntimeError("requested grains.out file does not exist!")
        
    #dictionary of what column in grains.out corresponds to what variable    
    grain_vars_ind = {
      "completeness": 1,
      "chisq": 2,
      "exp_map_c_0": 3,
      "exp_map_c_1": 4,
      "exp_map_c_2": 5,
      "t_vec_c_0": 6,
      "t_vec_c_1": 7,
      "t_vec_c_2": 8,
      "inv_V_s_0_0": 9,
      "inv_V_s_1_1": 10,
      "inv_V_s_2_2": 11,
      "inv_V_s_1_2_sqrt2": 12,
      "inv_V_s_0_2_sqrt2": 13,
      "ln_V_s_0_0": 15,
      "ln_V_s_1_1": 16,
      "ln_V_s_2_2": 17,
      "ln_V_s_1_2": 18,
      "ln_V_s_0_2": 20,
      "ln_V_s_0_1": 21 }
      
    #make sure var_for_hist appears in the dictionary
    if var_for_hist in grain_vars_ind:
        print("will plot histogram of variable " + var_for_hist + " which is column " + str(grain_vars_ind[var_for_hist]))
    else:
        raise RuntimeError("requested variable to histogram is not found in grains.out")
    
    #construct the output filename
    if output_fname == "":
        output_fname = os.path.join(grains_fpath, var_for_hist + ".png")
        print("no output filename specified, will save output to: " + output_fname)
    else:
        output_fname = os.path.join(grains_fpath, output_fname + ".png")
        print("will save output to: " + output_fname)

    #read in the grains.out file
    ff_data = np.loadtxt(grains_full_fname)
    #ff_data is a [number of grains] x 21 ndarray 
    #ff_data[n][0] = index of grain n
    #ff_data[n][1] = completeness for grain n
    #ff_data[n][2] = chi^2 for grain n
    #ff_data[n][3, 4, 5] = exp_map_c[0,1,2] orientations for grain n
    #ff_data[n][6, 7, 8] = t_vec_c[0,1,2]
    #ff_data[n][9, 10, 11] = inv(V_s[0,0],[1,1],[2,2]
    #etc... 
    
    print("specified grains.out contains " + str(np.max(ff_data[:,0])) + " grains")
    print("minimum " + var_for_hist + ": " + str(np.max(ff_data[:,grain_vars_ind[var_for_hist]])))
    print("maximum " + var_for_hist + ": " + str(np.min(ff_data[:,grain_vars_ind[var_for_hist]])))
    
    #histogram the requested value
    fig = plt.figure(figsize =(10,7))
    plt.hist(ff_data[:,grain_vars_ind[var_for_hist]],100)
    plt.title(grains_fname + ' ' + var_for_hist)
    if (xmin!=-1):
        plt.xlim(xmin, xmax)
    plt.show
    plt.ylabel('[N]')
    plt.xlabel(var_for_hist)
    plt.savefig(output_fname)
    
    
