#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:02:52 2023

Purpose: Two-step Lorentzian fitting for z-spectra, adapted from Kevin Godines' implementation.

@author: JWW
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

##Set variables for testing##
cest_offsets = np.linspace(-4,4,num=41)
zspecs = np.random.randint(1, 101, size=(128,128,41,1,1))
cutoff = 1.4

##Starting points for curve fitting: amplitude, FWHM, peak center##
p0_water = [1, 0.8, 0.2]
p0_mt = [0.15, 40, -1]
p0_noe = [0.05, 1, -2.75]
p0_creatine = [0.05, 0.5, 2.6]
p0_amide = [0.05, 1.5, 3.5]
##Lower bounds for curve fitting##
lb_water = [1, 0.02, 0.01]
lb_mt = [0.0, 30, -2.5]
lb_noe = [0.0, 1, -4.5]
lb_creatine = [0.0, 0.1, 1.6]
lb_amide = [0.0, 0.2, 3.2]
##Upper bounds for curve fitting##
ub_water = [1, 1, 10]
ub_mt = [0.5, 60, 0]
ub_noe = [0.25, 5, -1.5]
ub_creatine = [0.5, 5, 3.0]
ub_amide = [0.3, 5, 4.0]

##Exclude points in CEST metabolites region for intitial fit step##
def cutoffs(cutoff, cest_offsets, zspecs):
    mask = np.ones(np.shape(cest_offsets))
    mask = np.ma.masked_where(np.logical_or(cest_offsets<-1*cutoff, cest_offsets>cutoff), mask)
    masked_offsets = cest_offsets*mask
    masked_zspecs = zspecs*mask[:, np.newaxis, np.newaxis]
    return masked_offsets, masked_zspecs

##Lorentzian lineshape definition with FWHM##
def lorentzian(x, amp, fwhm, center):
    return amp * fwhm**2/(fwhm**2 + (x - center)**2)

def water_mt_background(x, water_params, mt_params):
    water = lorentzian(x, *water_params)
    mt = lorentzian(x, *mt_params)
    background = water + mt
    return water, mt, background
    

masked_offsets, masked_zspecs = cutoffs(cutoff, cest_offsets, zspecs)

water, mt, background = water_mt_background(masked_offsets, p0_water, p0_mt)

plt.plot(masked_offsets, water)
plt.plot(masked_offsets, mt)
plt.plot(masked_offsets, background)