#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:45:26 2023

@author: JWW
"""
import re
import numpy as np
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd

def get_paths_cest(acq_type):
    ##Get filepath for data directory##
    tkmb.showinfo('JCT', 'Select data directory', icon='info')
    data_directory = tk.filedialog.askdirectory()
    ##Get filepath for M0##
    tk.messagebox.showinfo('CEST 2Dseq', 'Select M0', icon='info')
    m0_path = tk.filedialog.askdirectory(initialdir = data_directory)
    ##Get filepath for  continuous CEST data##
    if acq_type == "c":
        tkmb.showinfo('JCT', 'Select CEST experiment', icon='info')
        cest_experiment = tk.filedialog.askdirectory(initialdir = data_directory)
        cest_experiment_name = re.search('/2(.+?)/', cest_experiment)
        cest_experiment_name = '2' + str(cest_experiment_name.group(1))
        cest_paths = [cest_experiment]
    elif acq_type == "s":
        tkmb.showinfo('JCT', 'Select CEST experiment w/ offsets -4 to 4 ppm', icon='info')
        cest_experiment_mid = tk.filedialog.askdirectory(initialdir = data_directory)
        cest_experiment_name = re.search('/2(.+?)/', cest_experiment_mid)
        cest_experiment_name = '2' + str(cest_experiment_name.group(1))
        tkmb.showinfo('JCT', 'Select CEST experiment w/ offsets -10 to -5 ppm', icon='info')
        cest_experiment_neg = tk.filedialog.askdirectory(initialdir = data_directory)
        tkmb.showinfo('JCT', 'Select CEST experiment w/ offsets 5 to 10', icon='info')
        cest_experiment_pos = tk.filedialog.askdirectory(initialdir = data_directory)   
        cest_paths = [cest_experiment_neg, cest_experiment_mid, cest_experiment_pos]
    ##Get filepath for WASSR data##
    tkmb.showinfo('JCT', 'Select WASSR experiment', icon='info')
    wassr_experiment = tk.filedialog.askdirectory(initialdir = data_directory)
    wassr_paths = [wassr_experiment]
    ##Return filepaths##
    return data_directory, cest_experiment_name, cest_paths, wassr_paths, m0_path

def load_2dseq_b1(data_directory):
    methods = []
    fids = []
    angles = []
    ##Get directories##
    tkmb.showinfo('JCT', 'Select 60 degree FA', icon = 'info')
    angle_60_directory = tk.filedialog.askdirectory(initialdir = data_directory)
    tkmb.showinfo('JCT', 'Select 120 degree FA', icon = 'info')
    angle_120_directory = tk.filedialog.askdirectory(initialdir = data_directory)
    paths = [angle_60_directory, angle_120_directory]
    ##Load file contents##
    for path in paths:
        filepath_2dseq = path+'/pdata/1/2dseq'
        filepath_method = path+'/method'
        method = open(filepath_method)
        fid = open(filepath_2dseq, 'rb')
        methods.append(method)
        fids.append(fid)
    for line in methods[0]:
        if '$PVM_Matrix' in line:
            matrix = next(methods[0]).split()
            matrix = [eval(i) for i in matrix]
        if '$PVM_SPackArrNSlices' in line:
            slices = eval(next(methods[0]))
    for i in range(np.size(fids)):
        image = np.fromfile(fids[i], np.int16)
        image = np.reshape(image, (matrix[0], matrix[1], slices), order = 'F')
        image = np.rot90(image, k=1, axes=(1,0))  
        angles.append(image)
    return angles

def load_2dseq_cest(exp_paths, m0_path):
    ##Load file contents to list##
    methods = []
    fids = []    
    parameters = []
    images = []
    for path in exp_paths:
        filepath_2dseq = path+'/pdata/1/2dseq'
        filepath_method = path+'/method'
        method = open(filepath_method)
        fid = open(filepath_2dseq, 'rb')
        methods.append(method)
        fids.append(fid)
    m0_fid = open(m0_path+'/pdata/1/2dseq', 'rb')
    ##Find lines with important parameters, save parameters to variables##
    for method in methods:
        parameter_dct = {}
        for line in method:
            if '$PVM_FrqRef=' in line:
                hz_ref = next(method).split()
                hz_ref = int(eval(hz_ref[0]))
                parameter_dct["Ref frequency"] = hz_ref
            if '$PVM_Matrix' in line:
                matrix = next(method).split()
                matrix = [eval(i) for i in matrix]
                parameter_dct["Matrix"] = matrix
            if '$PVM_SPackArrNSlices' in line:
                slices = eval(next(method))
                parameter_dct["Slices"] = slices
            if '$Number_Offset_Experiments' in line:
                n1 = eval(line.replace('##$Number_Offset_Experiments=',''))
                parameter_dct["Offsets"] = n1
            if '$Min_Cest_Offset' in line:
                hz_start = eval(line.replace('##$Min_Cest_Offset=',''))
                parameter_dct["Min offset"] = hz_start
            if '$Max_Cest_Offset' in line:
                hz_end = eval(line.replace('##$Max_Cest_Offset=',''))
                parameter_dct["Max offset"] = hz_end
            if '$Offset_Step_Hz' in line:
                hz_inc = eval(line.replace('##$Offset_Step_Hz=',''))
                parameter_dct["Offset step"] = hz_inc
        parameters.append(parameter_dct)
    ##Load raw data into array and reshape##
    m0_image = np.fromfile(m0_fid, np.int16)
    m0_image = np.reshape(m0_image, (parameters[0]['Matrix'][0], parameters[0]['Matrix'][0], parameters[0]['Slices']), order = 'F')
    for i in range(np.size(fids)):
        image = np.fromfile(fids[i], np.int16)
        image = np.reshape(image, (parameters[i]['Matrix'][0], parameters[i]['Matrix'][0], parameters[i]['Slices'], parameters[i]['Offsets']), order = 'F')
        images.append(image)
    ##Add segmented z-spectra together##
    zspecs = np.concatenate(images, axis = 3)
    ##Create offsets list##
    ppm_list = []
    for i in range(np.size(parameters)):
        ref = parameters[i]['Ref frequency']
        ppm = np.linspace(parameters[i]['Min offset']/ref, parameters[i]['Max offset']/ref, parameters[i]['Offsets'], endpoint=True)
        ppm_list.append(ppm)
    ppm_list = np.concatenate(ppm_list)
    ##Swap axes for order (matrix_x, matrix_y, offsets, slices)
    zspecs = np.swapaxes(zspecs, 2, 3)
    ##Flip image ordering to match NMR convention##
    # zspecs = np.flip(zspecs, axis=2)
    ##Flip offset list to match ordering##
    # ppm_list = np.flip(ppm_list)   
    ##Rotate 90-degrees##        
    m0_image = np.rot90(m0_image, k=1, axes=(1,0))        
    zspecs = np.rot90(zspecs, k=1, axes=(1,0))
    # ##Return images and offset list##
    return m0_image, zspecs, ppm_list    