#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:02:52 2023

Purpose: Two-step Lorentzian fitting for z-spectra, adapted from Kevin Godines' implementation.

@author: JWW
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline, splev, splrep 
##Set variables for testing##
# cest_offsets = np.linspace(-4,4,num=41)
# zspecs = np.load('test_zspec.npy')
# zspecs = zspecs[:,0,0]

##Starting points for curve fitting: amplitude, FWHM, peak center##
p0_water = [0.8, 0.2, 0]
p0_mt = [0.15, 40, -1]
p0_noe = [0.05, 1, -2.75]
p0_creatine = [0.05, 0.5, 2.6]
p0_amide = [0.05, 1.5, 3.5]
##Lower bounds for curve fitting##
lb_water = [0.02, 0.01, -0.01]
lb_mt = [0.0, 30, -2.5]
lb_noe = [0.0, 1, -4.5]
lb_creatine = [0.0, 0.1, 1.6]
lb_amide = [0.0, 0.2, 3.2]
##Upper bounds for curve fitting##
ub_water = [1, 10, 0.01]
ub_mt = [0.5, 60, 0]
ub_noe = [0.25, 5, -1.5]
ub_creatine = [0.5, 5, 3.0]
ub_amide = [0.3, 5, 4.0]

##Combine for curve fitting##
#Step 1
p0_1 = p0_water + p0_mt
lb_1 = lb_water + lb_mt
ub_1 = ub_water + ub_mt 
#Step 2
p0_2 = p0_noe + p0_creatine + p0_amide
lb_2 = lb_noe + lb_creatine + lb_amide
ub_2 = ub_noe + ub_creatine + ub_amide

##Interpolate offsets##
# offsets_interp = np.linspace(cest_offsets[0], cest_offsets[-1], 1000, endpoint=True)

##Exclude points in CEST metabolites region for intitial fit step##
def cutoffs(cest_offsets, zspecs, cutoff):
    mask = np.ones(np.shape(cest_offsets))
    mask = np.ma.masked_where(np.logical_or(cest_offsets<-1*cutoff, cest_offsets>cutoff), mask)
    masked_offsets = cest_offsets*mask
    masked_zspecs = zspecs*mask
    return masked_offsets, masked_zspecs

##Lorentzian lineshape definition with FWHM##
def lorentzian(x, amp, fwhm, offset):
    return amp*0.5*fwhm**2/((x-offset)**2+0.5*fwhm**2)


##2-step fitting##
def step_1_fit(x, *fit_parameters):
    water_fit = lorentzian(x, fit_parameters[0], fit_parameters[1], fit_parameters[2])
    mt_fit = lorentzian(x, fit_parameters[3], fit_parameters[4], fit_parameters[5])
    fit = 1 - water_fit - mt_fit
    return fit

def step_2_fit(x, *fit_parameters):
    noe_fit = lorentzian(x, fit_parameters[0], fit_parameters[1], fit_parameters[2])
    creatine_fit = lorentzian(x, fit_parameters[3], fit_parameters[4], fit_parameters[5])
    amide_fit = lorentzian(x, fit_parameters[6], fit_parameters[7], fit_parameters[8])
    fit = noe_fit + creatine_fit + amide_fit
    return fit

##Calculate fits and plot Lorentzians##
def fitting(cest_offsets, zspecs):
    ##Global curve fitting variables##
    global p0_1, p0_2, lb_1, lb_2, ub_1, ub_2
    ##Check that there's actually data##
    if zspecs[0] == 0:
        fit_1 = np.zeros(6)
        fit_2 = np.zeros(9)
        water_fit = np.zeros_like(zspecs)
        mt_fit = np.zeros_like(zspecs)
        noe_fit = np.zeros_like(zspecs)
        creatine_fit = np.zeros_like(zspecs)
        amide_fit = np.zeros_like(zspecs)
    else:
        ##Mask offsets outside of range for first step##
        masked_offsets, masked_zspecs = cutoffs(cest_offsets, zspecs, cutoff=1.4)
        ##Step 1##
        fit_1, _ = curve_fit(step_1_fit, masked_offsets, masked_zspecs, p0=p0_1, bounds=(lb_1, ub_1))
        ##Calculate water and MT fits from parameters##
        water_fit = lorentzian(cest_offsets, fit_1[0], fit_1[1], fit_1[2])
        mt_fit = lorentzian(cest_offsets, fit_1[3], fit_1[4], fit_1[5])
        ##Calculate background and Lorentzian difference##
        background = water_fit + mt_fit
        lorentzian_difference = 1 - (zspecs + background)
        ##Step 2##
        fit_2, _ = curve_fit(step_2_fit, cest_offsets, lorentzian_difference, p0=p0_2, bounds=(lb_2, ub_2), maxfev = 10000)
        ##Calulate NOE, creatine, and amide fits from parameters##
        noe_fit = lorentzian(cest_offsets, fit_2[0], fit_2[1], fit_2[2])
        creatine_fit = lorentzian(cest_offsets, fit_2[3], fit_2[4], fit_2[5])
        amide_fit = lorentzian(cest_offsets, fit_2[6], fit_2[7], fit_2[8])
    ##Organize##
    parameters = {"Water":[fit_1[0], fit_1[1], fit_1[2]], "MT":[fit_1[3], fit_1[4], fit_1[5]], "NOE":[fit_2[0], fit_2[1], fit_2[2]], "Creatine":[fit_2[3], fit_2[4], fit_2[5]], "Amide":[fit_2[6], fit_2[7], fit_2[8]]}
    fits = {"Water":water_fit, "MT":mt_fit, "NOE":noe_fit, "Creatine":creatine_fit, "Amide":amide_fit}
    return parameters, fits
    
##Pipelines for single spectrum and full image (voxelwise)##
def image_data_pipeline(zspecs, offsets):
    matrix_x = np.size(zspecs,0)
    matrix_y = np.size(zspecs,1)
    slices = np.size(zspecs, 3)
    parameters = []
    fits = []
    for i in range(matrix_x):
        for j in range(matrix_y):
            for k in range(slices):
                zspec = zspecs[i,j,:,k]
                p,f = fitting(offsets, zspec)
                parameters.append(p)
                fits.append(f)
    parameters = np.array(parameters)
    fits = np.array(fits)
    parameters = parameters.reshape((matrix_x, matrix_y, slices))
    fits = fits.reshape((matrix_x, matrix_y, slices))
    return parameters, fits

def single_spectrum_pipeline(zspecs, offsets): 
    slices = np.size(zspecs,1)
    region = np.size(zspecs,2)
    parameters = []
    fits = []
    for i in range(slices):
        for j in range(region):
            zspec = zspecs[:,i,j]
            p,f = fitting(offsets, zspec)
            parameters.append(p)
            fits.append(f)
    parameters = np.array(parameters)
    fits = np.array(fits)
    parameters = parameters.reshape((slices, region))
    fits = fits.reshape((slices, region))
    return parameters, fits