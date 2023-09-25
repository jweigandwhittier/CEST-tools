#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:43:30 2023

@author: JWW
"""
from scipy.interpolate import CubicSpline, splev, splrep
import numpy as np

##Interpolate WASSR spectrum for B0 correction##
def interpolate_wassr(offsets, zspec):
    ##Flip axes for cubic spline interpolation##
    offsets = np.flip(offsets)
    zspec = np.flip(zspec, axis=2)
    ##Reshape image for easier iteration, create empty array for interpolated spectra and interpolated offsets##
    matrix_x = np.size(zspec, 0)    
    matrix_y = np.size(zspec, 1)
    zspec = np.reshape(zspec,(matrix_x*matrix_y, np.size(zspec,2), -1)) 
    offsets_interp = np.linspace(-0.25, 0.25, 100)
    points = np.size(offsets_interp)
    zspecs_interp = np.zeros((np.size(zspec,0), points, np.size(zspec,2)))
    ##Iterate through voxels --> slices, add interpolated spectra to empty array##
    for i in range(np.size(zspec,0)):
        for j in range(np.size(zspec,2)):
            spline = CubicSpline(offsets,zspec[i,:,j])
            zspec_interp = spline(offsets_interp)
            zspecs_interp[i,:,j] = zspec_interp
    ##Flip back to original orientation and reshape##
    zspecs_interp = np.flip(zspecs_interp, axis=1)
    offsets_interp = np.flip(offsets_interp)
    zspecs_interp = np.reshape(zspecs_interp, (matrix_x, matrix_y, points, -1))
    return offsets_interp, zspecs_interp

##Get B0 map from WASSR##
def wassr_b0_map(offsets_interp, wassr_interp):
    b0_map = np.zeros_like(wassr_interp[:,:,0,:])
    for i in range(np.size(b0_map, 0)):
        for j in range(np.size(b0_map, 1)):
            for k in range(np.size(b0_map, 2)):
                index = np.argmin(wassr_interp[i,j,:,k])
                b0_shift = offsets_interp[index]
                b0_map[i,j,k] = b0_shift
    return b0_map
    
##Apply B0 correction to CEST spectrum##
def b0_correction(offsets, zspec, b0_map):
    ##Reshape B0 map and Z-spectra##
    matrix_x = np.size(zspec, 0)
    matrix_y = np.size(zspec, 1)
    points = np.size(zspec, 2)
    zspec = np.reshape(zspec, (matrix_x*matrix_y, points, -1))
    b0_map = np.reshape(b0_map, (matrix_x*matrix_y, -1))
    #Flip for interpolation##
    zspec = np.flip(zspec, axis=1)
    offsets = np.flip(offsets)
    ##Iterate through each spectrum with corresponding B0 shift##
    for i in range(np.size(b0_map, 0)):
        for j in range(np.size(b0_map, 1)):
            shift_ppm = b0_map[i,j]
            spectrum = zspec[i,:,j]
            tck = splrep(offsets, spectrum, s=0)
            shifted_spectrum = np.squeeze(splev(offsets+shift_ppm, tck, der=0))
            zspec[i,:,j] = shifted_spectrum
    ##Flip back and reshape##
    zspec = np.flip(zspec, axis=1)
    zspec = np.reshape(zspec, (matrix_x, matrix_y, points, -1))
    return zspec  