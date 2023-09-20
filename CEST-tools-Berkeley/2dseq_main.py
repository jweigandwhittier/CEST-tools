#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:29:21 2023

Purpose: Read 2dseq files from Bruker scanners and generate Z-spectra. 2dseq loading and organization based on Matlab code by OP.
WASSR and interpolation methods from Mina Kim et al, MRM 61(6) pp. 1441-1450
2-step Lorentzian fit method from Kevin Goodines et al.

@author: JWW
"""
import re
import os
import platform
import ctypes
import matplotlib.pyplot as plt
from resources.load_2dseq import get_paths, load_2dseq
from resources.roi_selector import define_noise_masks, apply_noise_masks, spectrum_roi_phantom, spectrum_roi_cardiac
from resources.b0_correction import interpolate_wassr, wassr_b0_map, b0_correction
from resources.cest_analysis import zspec_avg, zspec_voxel, plt_avg
import tkinter as tk

##Get CWD##
path = os.getcwd()

##Identify OS##
platform = platform.system()

##Set up tkinter##
root = tk.Tk()
root.withdraw()

##Icon assignment per OS##
if platform == 'Windows':
    root.iconbitmap = (path+'/resources/icons/icon.ico')
else:
    icon = tk.Image('photo', file=path+'/resources/icons/icon.png')
    root.iconphoto(True, icon)
    
###Prompt for CETS acquisition type###
def choose_acq_type():
    acq_type = input("For continuous type 'c', for segmented type 's': ")
    if acq_type == "c" or acq_type == "s":
        cest_experiment_name, cest_paths, wassr_paths, m0_path = get_paths(acq_type)
        return cest_experiment_name, cest_paths, wassr_paths, m0_path
    else:
        print("Please choose a valid acquisition type.")
        return choose_image_type()

cest_experiment_name, cest_paths, wassr_paths, m0_path = choose_acq_type()

##Load data from 2dseq files##
m0_image, cest_zspecs, cest_offsets = load_2dseq(cest_paths, m0_path)
m0_image, wassr_zspecs, wassr_offsets = load_2dseq(wassr_paths, m0_path)

##Get noise mask and apply to WASSR data##
noise_mask = define_noise_masks(m0_image, threshold=1)
masked_wassr = apply_noise_masks(m0_image, wassr_zspecs, noise_mask)

##Interpolate masked WASSR spectrum##
wassr_offsets_interp, wassr_zspecs_interp = interpolate_wassr(wassr_offsets, masked_wassr)

##Generate B0 map and perform B0 correction on CEST data##
b0_map = wassr_b0_map(wassr_offsets_interp, wassr_zspecs_interp)

##Generate B1 map from double angle images##

##Apply B0 correction##
def choose_corrections(cest_zspecs):
    b0_prompt = input("Perform B0 correction from WASSR? ('y' or 'n'):")
    b1_prompt = input("Perform B1 correction from B1 map? ('y' or 'n':")
    if b0_prompt == 'y':
        cest_zspecs = b0_correction(cest_offsets, cest_zspecs, b0_map)
    elif b0_prompt == 'n':
        cest_zspecs = cest_zspecs
    else:
        print("Please type 'y' or 'n'.")
    if b1_prompt == 'y':
        print("Sorry! B1 correction not implemented yet.")
    elif b1_prompt == 'n':
        print("That's ok, I can't do B1 correction it regardless.")
    else:
        print("Please type 'y' or 'n'.")
    return cest_zspecs

cest_zspecs = choose_corrections(cest_zspecs)
    
##Mask corrected CEST images##
masked_cest = apply_noise_masks(m0_image, cest_zspecs, noise_mask)

###Get ROIs for CEST images###
def choose_image_type():
    image_type = input("For cardiac type 'c', for phantom type 'p': ")   
    if image_type == "p":
        cest_roi = spectrum_roi_phantom(m0_image, masked_cest)
        return cest_roi, image_type
    elif image_type == "c":
        cest_roi = spectrum_roi_cardiac(m0_image, masked_cest)
        return cest_roi, image_type
    else:
        print("You must choose a valid image type.")
        return choose_image_type()

cest_masks, image_type = choose_image_type()
    
###Calculate Z-specs/Lorentzian fits###
def choose_calc():
    y_or_n = input("Do you want to calculate avg. z-spectrum over entire region? ('y' or 'n'): ")
    if y_or_n == "y":
        voxel_zspec = zspec_voxel(cest_masks, m0_image)
        avg_zspec = zspec_avg(voxel_zspec)
        plt_avg(avg_zspec, cest_offsets, image_type)
        return voxel_zspec, avg_zspec
    elif y_or_n == "n":
        voxel_zspec = zspec_voxel(cest_masks, m0_image)
        avg_zspec = None
        return voxel_zspec, avg_zspec
    else:
        print("Please type 'y' or 'n'.")
        return choose_calc
    
voxel_zpec, avg_zpec = choose_calc()