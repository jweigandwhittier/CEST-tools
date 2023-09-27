#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 10:29:03 2023

Purpose: Plot field maps and fitted z-spectra amplitudes (per pool). Colormap implementation from code by OP. 

@author: JWW

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def plot_avg_fits(x, fits, plots_dir):
    for i in range(len(fits)):
        for j in range(len(fits[i])):
            fit = fits[i][j]
            fig, ax = plt.subplots(1,1)
            fig.suptitle("5-pool Lorentzian Fits")
            ax.plot(x, fit['Water'], label = "Water")
            ax.plot(x, fit['MT'], label = "MT")
            ax.plot(x, fit['NOE'], label = "NOE")
            ax.plot(x, fit['Creatine'], label = "Creatine")
            ax.plot(x, fit['Amide'], label = "Amide")
            ax.legend()
            ##Show##
            plt.show()
            ##Save plot##
            to_save = plots_dir + "/avg_fits_region%i.pdf" % j
            fig.savefig(to_save)
        
def plot_b0_only(b0_map, plots_dir):
    ##Set colormap##
    original_map = plt.cm.get_cmap('viridis')
    color_mat = original_map(np.arange(original_map.N))
    color_mat[0, 0:3] = 0  
    b_viridis = mcolors.LinearSegmentedColormap.from_list('colormap', color_mat)
    ##Values for indexing##
    slices = np.size(b0_map, axis = 2)
    ##Set up subplots##
    fig, axs = plt.subplots(slices, 1, layout = "tight")
    if slices > 1:
        ##Add titles##
        fig.suptitle("Field Maps")
        axs[0,0].set_title("B0")
        ##Plot maps##
        for i in range(slices):
            axs[slices,0].imshow(b0_map[:,:,slices], cmap = b_viridis)
            axs[slice,0].set_ylabel("Slice %i" % (i+1))
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([])     
    else:
        ##Add titles##
        fig.suptitle("Field Maps")
        axs[0].set_title("B0")
        ##Plot maps##
        axs[0].imshow(b0_map[:,:,0])
        axs[0].set_ylabel("Slice 1")
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([]) 
    ##Show##
    plt.show()
    ##Save plot##
    to_save = plots_dir + "/b0_map.pdf"
    fig.savefig(to_save)
    

def plot_field_maps(b0_map, b1_map, plots_dir):
    ##Set colormap##
    original_map = plt.cm.get_cmap('viridis')
    color_mat = original_map(np.arange(original_map.N))
    color_mat[0, 0:3] = 0  
    b_viridis = mcolors.LinearSegmentedColormap.from_list('colormap', color_mat)
    ##Values for indexing##
    slices = np.size(b0_map, axis = 2)
    ##Set up subplots##
    fig, axs = plt.subplots(slices, 2, layout = "tight")
    if slices > 1:
        ##Add titles##
        fig.suptitle("Field Maps")
        axs[0,0].set_title("B0")
        axs[0,1].set_title("B1")
        ##Plot maps##
        for i in range(slices):
            axs[slices,0].imshow(b0_map[:,:,slices], cmap = b_viridis)
            axs[slices,1].imshow(b1_map[:,:,slices], cmap = b_viridis)
            axs[slice,0].set_ylabel("Slice %i" % (i+1))
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([])     
    else:
        ##Add titles##
        fig.suptitle("Field Maps")
        axs[0].set_title("B0")
        axs[1].set_title("B1")
        ##Plot maps##
        axs[0].imshow(b0_map[:,:,0])
        axs[1].imshow(b1_map[:,:,0])
        axs[0].set_ylabel("Slice 1")
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([]) 
    ##Show##
    plt.show()
    ##Save plot##
    to_save = plots_dir + "/field_maps.pdf"
    fig.savefig(to_save)
    
def plot_amplitudes(parameters, plots_dir):
    ##Set colormap##
    original_map = plt.cm.get_cmap('viridis')
    color_mat = original_map(np.arange(original_map.N))
    color_mat[0, 0:3] = 0  
    b_viridis = mcolors.LinearSegmentedColormap.from_list('colormap', color_mat)
    ##Values for indexing##
    matrix_x = np.size(parameters, 0)
    matrix_y = np.size(parameters, 1)
    slices = np.size(parameters, 2)
    ##Get values from dicts##
    parameters = parameters.flatten()
    water = [d['Water'][0] for d in parameters]
    mt = [d['MT'][0] for d in parameters]
    noe = [d['NOE'][0] for d in parameters]
    creatine = [d['Creatine'][0] for d in parameters]
    amide = [d['Amide'][0] for d in parameters]
    ##Reshape back to images##
    water = np.reshape(water, (matrix_x, matrix_y, slices))
    mt = np.reshape(mt, (matrix_x, matrix_y, slices))
    noe = np.reshape(noe, (matrix_x, matrix_y, slices))
    creatine = np.reshape(creatine, (matrix_x, matrix_y, slices))
    amide = np.reshape(amide, (matrix_x, matrix_y, slices))
    ##Set up subplots##
    fig, axs = plt.subplots(slices, 5, layout = "tight")
    if slices > 1:
        ##Add titles##
        fig.suptitle("Amplitudes (%)")
        axs[0,0].set_title("Water")
        axs[0,1].set_title("MT")
        axs[0,2].set_title("NOE")
        axs[0,3].set_title("Creatine")
        axs[0,4].set_title("Amide")
        ##Plot maps##
        for i in range(slices):
            axs[slices,0].imshow(water[:,:,slices], cmap = b_viridis)
            axs[slices,1].imshow(mt[:,:,slices], cmap = b_viridis)
            axs[slices,2].imshow(noe[:,:,slices], cmap = b_viridis)
            axs[slices,3].imshow(creatine[:,:,slices], cmap = b_viridis)
            axs[slices,4].imshow(amide[:,:,slices], cmap = b_viridis)
            axs[slice,0].set_ylabel("Slice %i" % (i+1))
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([])     
    else:
        ##Add titles##
        fig.suptitle("Amplitudes (%)")
        axs[0].set_title("Water")
        axs[1].set_title("MT")
        axs[2].set_title("NOE")
        axs[3].set_title("Creatine")
        axs[4].set_title("Amide")
        ##Plot maps##
        axs[0].imshow(water[:,:,0], cmap = b_viridis)
        axs[1].imshow(mt[:,:,0], cmap = b_viridis)
        axs[2].imshow(noe[:,:,0], cmap = b_viridis)
        axs[3].imshow(creatine[:,:,0], cmap = b_viridis)
        axs[4].imshow(amide[:,:,0], cmap = b_viridis)
        axs[0].set_ylabel("Slice 1")
        for ax in axs:
            ax.set_xticks([])
            ax.set_yticks([]) 
    ##Show##
    plt.show()
    ##Save plot##
    to_save = plots_dir + "/amplitudes.pdf"
    fig.savefig(to_save)