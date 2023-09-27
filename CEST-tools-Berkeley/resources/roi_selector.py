#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 17:05:03 2023

@author: JWW
"""
import matplotlib.pyplot as plt
import numpy as np
from roipoly import RoiPoly, MultiRoi

##Define threshold for noice mask##
def define_noise_masks(image, threshold):
    imslice = image[:,:,0]
    image_kw = dict(xticks=[], yticks=[], title ='Draw background noise ROI\nRight click to confirm')
    fig,ax = plt.subplots(subplot_kw=image_kw)
    ax.imshow(imslice)
    roi = RoiPoly(color='r')
    mask = roi.get_mask(imslice)
    noise_mask = imslice[mask]
    N = np.std(noise_mask)*threshold
    plt.close(fig)
    return N

##Apply noise mask to data##
def apply_noise_masks(image, data, N):
    ##Define empty array for noise masks (per slice)##
    masks = np.zeros_like(image)
    ##Iterate through slices##
    for i in range(np.size(image, 2)):      
        imslice = data[:,:,:,i]
        ind = np.argwhere(imslice>N)
        for j in range(np.size(ind, 0)):
            indX = ind[j,0]
            indY = ind[j,1]
            masks[indX, indY, i] = 1
    n = np.size(data, axis=2)
    masks = np.stack([masks]*n, axis=-1)
    masks = np.swapaxes(masks, 2, 3)
    data = masks*data
    return data
    
##Draw ROIs for CEST analysis##
#Phantom#
def spectrum_roi_phantom(m0_image, data):
    ##Create list with user-defined number of ROIs##
    roi_list = []
    for i in range(int(input("Input # of ROIs: "))):
        roi_list.append("%i" % i)
    ##Empty list for masks##
    masks = np.zeros((data.shape + (len(roi_list),)))
    map_mask = np.zeros((m0_image.shape + (len(roi_list),)))
    ##Draw ROIs##
    for i in range(np.size(m0_image, 2)):
        imslice = m0_image[:,:,i]
        dataslice = data[:,:,:,i]
        image_kw = dict(xticks=[], yticks=[], title ='Click New ROI to start\nClick Finish when finished')
        fig, ax = plt.subplots(subplot_kw=image_kw)
        ax.imshow(imslice)
        multiroi_named = MultiRoi(roi_names=roi_list)
    ##For each ROI define mask##
        for name, roi in multiroi_named.rois.items():
            j = int(name)
            mask = roi.get_mask(imslice)
            mask_spectrum = np.stack([mask]*np.size(data, 2), -1)
            ##Apply masks to spectral data##
            data_mask = dataslice*mask_spectrum
            ##Store masks in array##
            masks[:,:,:,i,j] = data_mask
            map_mask[:,:,i,j] = mask
    return masks, map_mask

#Cardiac#
def spectrum_roi_cardiac(m0_image, data):
    roi_list = ['LV exterior', 'LV interior']
    masks = np.zeros((data.shape + (1,)))
    map_mask = np.zeros((m0_image.shape))
    for i in range(np.size(m0_image, 2)):
          imslice = m0_image[:,:,i]
          dataslice = data[:,:,:,i]
          image_kw = dict(xticks = [], yticks=[], title = 'Click New ROI to start\nClick Finish when finished')
          fig, ax = plt.subplots(subplot_kw=image_kw)
          ax.imshow(imslice)
          multiroi_named = MultiRoi(roi_names=roi_list)
          mask_exterior = multiroi_named.rois['LV exterior'].get_mask(imslice)
          mask_interior = multiroi_named.rois['LV interior'].get_mask(imslice)
          mask = np.logical_and(mask_exterior, np.logical_not(mask_interior))
          mask_spectrum = np.stack([mask]*np.size(data, 2), -1)
          ##Apply masks to spectral data##
          data_mask = dataslice*mask_spectrum
          ##Store masks in array##
          masks[:,:,:,i,0] = data_mask
          map_mask[:,:,i] = mask
    return masks, map_mask