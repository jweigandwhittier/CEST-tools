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

root = tk.Tk()
root.withdraw()

print("Select CEST experiment")
filepath_experiment = tk.filedialog.askdirectory(title="Select experiment folder")
experiment_name = re.search('/2(.+?)/', filepath_experiment)
experiment_name = '2' + str(experiment_name.group(1))

filepath_2dseq = filepath_experiment+'/pdata/1/2dseq'
filepath_method = filepath_experiment+'/method'

root.destroy()

method = open(filepath_method)
fid = open(filepath_2dseq, 'rb')

for line in method:
    if '$SatFreqExp' in line:
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

rawdata = np.fromfile(fid, np.int16)
rawdata = np.reshape(rawdata, (matrix[0], matrix[1], slices, niter), order='F')

offset_list = np.flip(np.arange(ppm_end, ppm_start+ppm_inc, ppm_inc))

n1 = niter - 1
image = np.zeros((matrix[0], matrix[1], n1, slices))
m0_image = np.zeros((matrix[0], matrix[1], slices))

for i in range(slices):
    m0_image[:,:,i] = rawdata[:,:,i,0]
    image[:,:,n1//2,i] = rawdata[:,:,i,n1]
    for j in range(1, niter//2):
        image[:,:,j-1,i] = rawdata[:,:,i,2*j-1]
    for j in range(1, n1//2):
        image[:,:,n1-j,i] = rawdata[:,:,i,2*j]
        
for i in range(slices):
    for j in range(n1):
        image[:,:,j,i] = np.nan_to_num(image[:,:,j,i]/m0_image[:,:,i])
        
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
    ax2.plot(offset_list, avg_zspec)
    zspec_list.append(avg_zspec)
    fig.canvas.draw_idle()
    array = array = np.negative(np.ones_like(image))
    
zspec_slice_list = []
    
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
    ax2.set_xlim([ppm_end, ppm_start])
    ax2.set_ylim([0,1.1])
    ax2.invert_xaxis()
    
    x,y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    pix = np.vstack((x.flatten(), y.flatten())).T
    
    lasso = LassoSelector(ax1, onselect)
    
    plt.show()
    
    # if keyboard.is_pressed('delete'):
        # ax2.clf()
        # zspec_list = []
    
    zspec_slice_list.append(zspec_list)
    
print("Reached the end of slice package")

with open('zspec_%s.txt' % experiment_name , 'wb') as file:
    pickle.dump(zspec_slice_list, file)
    
print("Saved ROIs")