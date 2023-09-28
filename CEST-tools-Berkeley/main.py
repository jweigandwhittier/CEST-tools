#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:29:21 2023

Purpose: Read 2dseq files from Bruker scanners and generate Z-spectra. 2dseq loading and organization based on Matlab code by OP.
WASSR and interpolation methods from Mina Kim et al, MRM 61(6) pp. 1441-1450
2-step Lorentzian fit method from Kevin Goodines et al.

@author: JWW
"""
import os
import platform
from resources.load_2dseq import get_paths_cest, load_2dseq_cest, load_2dseq_b1
from resources.roi_selector import define_noise_masks, apply_noise_masks, spectrum_roi_phantom, spectrum_roi_cardiac
from resources.b0_correction import interpolate_wassr, wassr_b0_map, b0_correction
from resources.b1_mapping import b1_mapping
from resources.cest_analysis import zspec_avg, zspec_voxel
from resources.cest_fitting import single_spectrum_pipeline, image_data_pipeline
from resources.plotting import plot_field_maps, plot_b0_only, plot_amplitudes, plot_avg_fits
import tkinter as tk
import numpy as np

##Supress runtime warnings (division warnings when normalizing z-spectra)##
import warnings
warnings.filterwarnings('ignore')

##Get CWD##
path = os.getcwd()

##Function for creating directory##
def make_directory(dir_name):
    if os.path.isdir(dir_name) == False:
        os.makedirs(dir_name)

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
    
###Prompt for CEST acquisition type###
def choose_acq_type():
    acq_type = input("For continuous type 'c', for segmented type 's': ")
    if acq_type == "c" or acq_type == "s":
        data_directory, cest_experiment_name, cest_paths, wassr_paths, m0_path = get_paths_cest(acq_type)
        return data_directory, cest_experiment_name, cest_paths, wassr_paths, m0_path
    else:
        print("Please choose a valid acquisition type.")
        return choose_acq_type()

data_directory, cest_experiment_name, cest_paths, wassr_paths, m0_path = choose_acq_type()

##Load data from 2dseq files##
m0_image, cest_zspecs, cest_offsets = load_2dseq_cest(cest_paths, m0_path)
m0_image, wassr_zspecs, wassr_offsets = load_2dseq_cest(wassr_paths, m0_path)

##Get noise mask and apply to WASSR data##
# noise_mask = define_noise_masks(m0_image, threshold=1)
# masked_wassr = apply_noise_masks(m0_image, wassr_zspecs, noise_mask)

##Interpolate masked WASSR spectrum##
# wassr_offsets_interp, wassr_zspecs_interp = interpolate_wassr(wassr_offsets, masked_wassr)
wassr_offsets_interp, wassr_zspecs_interp = interpolate_wassr(wassr_offsets, wassr_zspecs)

##Generate B0 map and perform B0 correction on CEST data##
b0_map = wassr_b0_map(wassr_offsets_interp, wassr_zspecs_interp)

##Generate B1 map from double angle images##
def choose_b1_map(cest_zspecs, data_directory):
    b1_prompt = input("Calculate B1 map from double angle? ('y' or 'n'): ")
    if b1_prompt == 'y':
        angles = load_2dseq_b1(data_directory)
        b1_map = b1_mapping(angles, cest_zspecs)
        print("B1 mapping finished.")
    elif b1_prompt == 'n':
        b1_map = None
    else:
        print("Please type 'y' or 'n'.")
        return choose_b1_map()
    return b1_map
b1_map = choose_b1_map(cest_zspecs, data_directory)

##Apply B0 correction##
def choose_corrections(cest_zspecs, b1_map):
    b0_prompt = input("Perform B0 correction from WASSR? ('y' or 'n'): ")
    if b0_prompt == 'y':
        cest_zspecs = b0_correction(cest_offsets, cest_zspecs, b0_map)
        print("B0 correction finished.")
    elif b0_prompt == 'n':
        cest_zspecs = cest_zspecs
    else:
        print("Please type 'y' or 'n'.")
    if b1_map is not None:
        b1_prompt = input("Perform B1 correction from B1 map? ('y' or 'n'): ")
        if b1_prompt == 'y':
            print("Sorry! B1 correction not implemented yet.")
        elif b1_prompt == 'n':
            print("That's ok, I can't do B1 correction regardless.")
        else:
            print("Please type 'y' or 'n'.")
            return choose_corrections()
    return cest_zspecs

cest_zspecs = choose_corrections(cest_zspecs, b1_map)
    
##Mask corrected CEST images##
# masked_cest = apply_noise_masks(m0_image, cest_zspecs, noise_mask)

###Get ROIs for CEST images###
def choose_image_type():
    image_type = input("For cardiac type 'c', for phantom type 'p': ")   
    if image_type == "p":
        # cest_roi = spectrum_roi_phantom(m0_image, masked_cest)
        cest_roi, map_mask = spectrum_roi_phantom(m0_image, cest_zspecs)
        return cest_roi, map_mask, image_type
    elif image_type == "c":
        # cest_roi = spectrum_roi_cardiac(m0_image, masked_cest)
        cest_roi, map_mask = spectrum_roi_cardiac(m0_image, cest_zspecs)
        return cest_roi, map_mask, image_type
    else:
        print("You must choose a valid image type.")
        return choose_image_type()

cest_masks, map_mask, image_type = choose_image_type()

###Apply masks to field maps###
b0_map *= map_mask
if b1_map is not None:
    b1_map *= map_mask
    
###Calculate Z-specs###
def choose_calc():
    y_or_n = input("Do you want to calculate avg. z-spectrum over entire region? ('y' or 'n'): ")
    if y_or_n == "y":
        voxel_zspec = zspec_voxel(cest_masks, m0_image)
        avg_zspec = zspec_avg(voxel_zspec)
        # plt_avg(avg_zspec, cest_offsets, image_type)
        return voxel_zspec, avg_zspec
    elif y_or_n == "n":
        voxel_zspec = zspec_voxel(cest_masks, m0_image)
        avg_zspec = None
        return voxel_zspec, avg_zspec
    else:
        print("Please type 'y' or 'n'.")
        return choose_calc
    
voxel_zspec, avg_zspec = choose_calc()

###Merge region ROIs###
voxel_zspec = voxel_zspec.sum(axis=4)

###Lorentzian fitting###
if avg_zspec is not None:
    avg_parameters, avg_fits = single_spectrum_pipeline(avg_zspec, cest_offsets)
    
voxel_parameters, voxel_fits = image_data_pipeline(voxel_zspec, cest_offsets)

###Save spectra; B0 & B1 maps; offsets; parameters; and fits###
voxel_dir = path + "/data/" + cest_experiment_name + "/voxel"
b0_b1_dir = path + "/data/" + cest_experiment_name + "/b0_b1"
offsets_dir = path + "/data/" + cest_experiment_name + "/offsets"
plots_dir = path + "/data/" + cest_experiment_name + "/plots"

make_directory(voxel_dir)
make_directory(b0_b1_dir)
make_directory(offsets_dir)
make_directory(plots_dir)

np.save(voxel_dir + '/voxel_zspec.npy', voxel_zspec)
np.save(voxel_dir + '/voxel_parameters.npy', voxel_parameters)
np.save(voxel_dir + '/voxel_fits.npy', voxel_fits)

np.save(b0_b1_dir + '/b0_map.npy', b0_map)
if b1_map is not None:
    np.save(b0_b1_dir + '/b1_map.npy', b1_map)

np.save(offsets_dir + '/offsets.npy', cest_offsets)

if avg_zspec is not None:
    avg_dir = path + "/data/" + cest_experiment_name + "/avg"
    make_directory(avg_dir)
    np.save(avg_dir + '/avg_zspec.npy', avg_zspec)
    np.save(avg_dir + '/avg_parameters.npy', avg_parameters)
    np.save(avg_dir + '/avg_fits.npy', avg_fits)
    plot_avg_fits(cest_offsets, avg_fits, plots_dir)
print("All fits and parameters completed and saved.")

def choose_plotting():
    y_or_n = input("Do you want to show and save field maps and amplitudes? ('y' or 'n'): ")
    if y_or_n == "y":
        if b1_map is not None:
            plot_field_maps(b0_map, b1_map, plots_dir)
        else:
            plot_b0_only(b0_map, plots_dir)
        plot_amplitudes(voxel_parameters, plots_dir)
        print("Plots saved. Finished!")
    elif y_or_n == "n":
        quit()
    else:
        print("Please type 'y' or 'n'.")
        return choose_calc()

choose_plotting()

root.destroy()