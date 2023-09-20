#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:45:26 2023

@author: JWW
"""
import re
import numpy as np
import tkinter as tk

def load_data():
    ##Get filepath for data directory##
    tk.messagebox.showinfo('CEST 2Dseq', 'Select data directory', icon='info')
    data_directory = tk.filedialog.askdirectory(title = "Select data directory")

    ##Get filepath for WASSR data##
    tk.messagebox.showinfo('CEST 2Dseq', 'Select WASSR experiment', icon='info')
    wassr_experiment = tk.filedialog.askdirectory(initialdir = data_directory)

    ##Get filepath for CEST data##
    tk.messagebox.showinfo('CEST 2Dseq', 'Select CEST experiment', icon='info')
    cest_experiment = tk.filedialog.askdirectory(initialdir = data_directory)
    cest_experiment_name = re.search('/2(.+?)/', cest_experiment)
    cest_experiment_name = '2' + str(cest_experiment_name.group(1))
    
    wassr_m0_image, wassr_zspecs, wassr_offsets = load_2dseq(wassr_experiment)
    cest_m0_image, cest_zspecs, cest_offsets = load_2dseq(cest_experiment)

def load_2dseq(filepath_experiment):
    ##Get filepath for 2dseq and method files##
    filepath_2dseq = filepath_experiment+'/pdata/1/2dseq'
    filepath_method = filepath_experiment+'/method'
    ##Open filepaths##
    method = open(filepath_method)
    fid = open(filepath_2dseq, 'rb')
    ##Find lines with important parameters, save parameters to variables##
    for line in method:
        if '$SatFreqExp' or '$Cest_Offsets' in line:
            niter = eval(line.replace('##$SatFreqExp=',''))
        if '$SatFreqStart' in line:
            ppm_start = eval(line.replace('##$SatFreqStart=',''))
        if '$SatFreqEnd' in line:
            ppm_end = eval(line.replace('##$SatFreqEnd=',''))
        if '$SatFreqInc' in line:
            ppm_inc = eval(line.replace('##$SatFreqInc=',''))
        if '$PVM_Matrix' in line:
            matrix = next(method).split()
            matrix = [eval(i) for i in matrix]
        if '$PVM_SPackArrNSlices' in line:
            slices = eval(next(method))
    ##Load raw data into array and reshape##
    rawdata = np.fromfile(fid, np.int16)
    rawdata = np.reshape(rawdata, (matrix[0], matrix[1], slices, niter), order='F')
    ##Flip offset list to match ordering##
    offset_list = np.flip(np.arange(ppm_end, ppm_start+ppm_inc, ppm_inc))
    ##Define variable for number of images in spectrum, define empty arrays for images##
    n1 = niter - 1
    image = np.zeros((matrix[0], matrix[1], n1, slices))
    m0_image = np.zeros((matrix[0], matrix[1], slices))
    ##Iterate through slices, write data to empty arrays##
    for i in range(slices):
        m0_image[:,:,i] = rawdata[:,:,i,0]
        image[:,:,n1//2,i] = rawdata[:,:,i,n1]
        for j in range(1, niter//2):
            image[:,:,j-1,i] = rawdata[:,:,i,2*j-1]
        for j in range(1, n1//2):
            image[:,:,n1-j,i] = rawdata[:,:,i,2*j]
    ##Normalize CEST images with M0##        
    # for i in range(slices):
    #     for j in range(n1):
    #         image[:,:,j,i] = np.nan_to_num(image[:,:,j,i]/m0_image[:,:,i])
    ##Rotate 90-degrees##        
    m0_image = np.rot90(m0_image, k=1, axes=(1,0))        
    zspecs = np.rot90(image, k=1, axes=(1,0))
    ##Return images and offset list##
    return m0_image, zspecs, offset_list