#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 13:18:47 2023

@author: JWW
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy

##Calculate averages over ROIs##
def zspec_avg(data):
    zspecs = []
    regions = []
    matrix = [np.size(data, 0), np.size(data, 1)]
    for i in range(np.size(data, 3)):
        for j in range(np.size(data, 4)):
            imslice = data[:,:,:,i,j]
            masked = np.ma.masked_equal(imslice, 0)
            avg_zspec = np.average(np.reshape(masked, (matrix[0]*matrix[1], -1)), axis=0)
            regions.append(avg_zspec)
        zspecs.append(regions)
    zspecs = np.array(zspecs)
    zspecs = zspecs.swapaxes(0,2)
    zspecs = zspecs.swapaxes(1,2)
    return zspecs

##Plot avg zspecs##
def plt_avg(zspecs, offsets, image_type):
    slices = np.size(zspecs, 1)
    fig, axs = plt.subplots(slices, sharex = True)
    fig.suptitle("Average z-spectrum per ROI")
    if slices == 1:
        axs.invert_xaxis()
    else:
        for ax in axs:
            ax.invert_xaxis()
    if image_type == "p":
        labels = []
        for i in range(np.size(zspecs, 2)):
            labels = []
            for i in range(np.size(zspecs, axis=2)):
                labels.append("Phantom ROI %i" % i)
    elif image_type == "c":
        labels = ["LV"]
    if slices == 1:
        for i in range(slices):
            axs.plot(offsets, zspecs[:,i,:])
            axs.set_title("Slice %i" % i)
            axs.legend(labels)
    else:
        axs[i].plot(offsets, zspecs[:,0,:])
        axs[i].set_title("Slice %i" % i)
        axs[i].legend(labels)
    fig.show()

##Normalize z-spectra voxelwise##
def zspec_voxel(data, m0_image):
    for i in range(np.size(data, 2)):
        for j in range(np.size(data, 3)):
            for k in range(np.size(data, 4)):
                data[:,:,i,j,k] = np.nan_to_num(data[:,:,i,j,k]/m0_image[:,:,j])
    return data   