#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:29:21 2023

Purpose: Read 2dseq files from Bruker scanners and generate Z-spectra. Based on Matlab code by OP.
ROI implementation adapted from https://gist.github.com/ofgulban/b620a2588c916e9b748aea4b3c108771

@author: JWW
"""
import os
import re
import linecache
import pickle
# import keyboard
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import tkinter as tk
from tkinter import filedialog

cest_path = '/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230913_111121_C57BL6J_F1_Test_1_5/11_CEST_5ppm_1uT'
m0_path = '/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230913_111121_C57BL6J_F1_Test_1_5/22_CEST_M0'

paths = [cest_path, m0_path]

##Load file contents to list##
methods = []
fids = []    
for path in paths:
    filepath_2dseq = path+'/pdata/1/2dseq'
    filepath_method = path+'/method'
    method = open(filepath_method)
    fid = open(filepath_2dseq, 'rb')
    methods.append(method)
    fids.append(fid)
##Find lines with important parameters, save parameters to variables##
for line in methods[0]:
    if '$PVM_FrqRef=' in line:
        hz_ref = next(methods[0]).split()
        hz_ref = eval(hz_ref[0])
    if '$PVM_Matrix' in line:
        matrix = next(methods[0]).split()
        matrix = [eval(i) for i in matrix]
    if '$PVM_SPackArrNSlices' in line:
        slices = eval(next(methods[0]))
    if '$Number_Offset_Experiments' in line:
        n1 = eval(line.replace('##$Number_Offset_Experiments=',''))
    if '$Min_Cest_Offset' in line:
        hz_start = eval(line.replace('##$Min_Cest_Offset=',''))
    if '$Max_Cest_Offset' in line:
        hz_end = eval(line.replace('##$Max_Cest_Offset=',''))
    if '$Offset_Step_Hz' in line:
        hz_inc = eval(line.replace('##$Offset_Step_Hz=',''))
##Load raw data into array and reshape##
imgdata = np.fromfile(fids[0], np.int16)
m0_data = np.fromfile(fids[1], np.int16)
imgdata = np.reshape(imgdata, (matrix[0], matrix[1], slices, n1), order='F')
m0_data = np.reshape(m0_data, (matrix[0], matrix[1], slices, 1), order = 'F')
##Flip offset list to match ordering##
ppm_list = np.flip(np.arange(hz_start, hz_end+hz_inc, hz_inc))
ppm_list = [x/hz_ref for x in ppm_list]
##Flip for convention (downfield --> upfield)##
imgdata = np.flip(imgdata, axis=3)
##Define empty arrays for images##
rawdata = np.concatenate((m0_data, imgdata), axis=3)
niter = n1+1
image = np.zeros((matrix[0], matrix[1], n1, slices))
m0_image = np.zeros((matrix[0], matrix[1], slices))
##Iterate through slices, write data to empty arrays##
for i in range(slices):
    m0_image[:,:,i] = rawdata[:,:,i,0]
    for j in range(n1):
        image[:,:,j,i] = rawdata[:,:,i,j]      
##Normalize CEST images with M0##        
for i in range(slices):
    for j in range(n1):
        image[:,:,j,i] = np.nan_to_num(image[:,:,j,i]/m0_image[:,:,i])
##Rotate 90-degrees##        
m0_image = np.rot90(m0_image, k=1, axes=(1,0))        
zspecs = np.rot90(image, k=1, axes=(1,0))
    
def update_array(array, indices):
    lin = np.arange(array.size)
    newarray = array.flatten()
    newarray[lin[indices]] = 1
    return newarray.reshape(array.shape)

def onselect(verts):
    global array, matrix, data, pix, n1, zspec_list
    p = Path(verts)
    ind = p.contains_points(pix, radius=1)
    array = update_array(array, ind)
    array = np.stack([array]*n1, axis=-1)
    avg = np.ma.masked_where(array<0, data)
    avg_zspec = np.average(np.reshape(avg, (matrix[0]*matrix[1], -1)), axis=0)
    avg_zspec = avg_zspec.compressed()
    ax2.plot(ppm_list, avg_zspec)
    zspec_list.append(avg_zspec)
    fig.canvas.draw_idle()
    array = array = np.negative(np.ones_like(image))
    
zspec_slice_list = []
ppm_start = ppm_list[0]
ppm_end = ppm_list[40]
    
for i in range(slices):
    image = m0_image[:,:,i]
    data = zspecs[:,:,:,i]
    array = np.negative(np.ones_like(image))
    zspec_list = []
    fig = plt.figure()
    fig.suptitle('Press Del to clear selections\nClose window for next slice')
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ax1.imshow(image)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax2.plot()
    ax2.set_xlim([ppm_start, ppm_end])
    ax2.set_ylim([0,1.1])
    # ax2.invert_xaxis()
    
    x,y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    pix = np.vstack((x.flatten(), y.flatten())).T
    
    lasso = LassoSelector(ax1, onselect)
    
    plt.show()
    
    # if keyboard.is_pressed('delete'):
        # ax2.clf()
        # zspec_list = []
    
    zspec_slice_list.append(zspec_list)
    
print("Reached the end of slice package")

with open('zspec.txt', 'wb') as file:
    pickle.dump(zspec_slice_list, file)
    
print("Saved ROIs")