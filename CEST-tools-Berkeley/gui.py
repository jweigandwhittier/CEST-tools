#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 16:06:55 2023

@author: jonah
"""
import os

import platform
from tkinter import *

from resources.load_2dseq import load_data, load_2dseq
from resources.roi_selector import define_noise_masks, apply_noise_masks, spectrum_roi_phantom
from resources.b0_correction import interpolate_wassr, wassr_b0_map, b0_correction
# from matplotlib.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

##Assign global variables (I probably want to get rid of this later)##
global cest_experiment_name, wassr_m0_image, wassr_zspecs, wassr_offsets, cest_m0_image, cest_zspecs, cest_offsets

##Get OS info##
path = os.getcwd()
platform = platform.system()

##Function for unlocking buttons##
# i=0
# button_state = ["disabled", "disabled", "disabled", "disabled"]

# def unlock_button(i):
#     button_state[i] = "normal"
#     i+=1
#     return button_state
    
##Set up root window##
root = Tk()
root.title("JCT")
root.geometry = ("500x200")
if platform == 'Windows':
    root.iconbitmap = (path+'/resources/icons/icon.ico')
else:
    icon = Image('photo', file=path+'/resources/icons/icon.png')
    root.iconphoto(True, icon)

load_button = Button(root, text = "Load data", command = load_data, height=6, width=12)

correction_button = Button(root, text = "B0 Correction", height=6, width=12)

roi_label = Label(root, text = "ROI Selection", height=3, width=12)
roi_button_1 = Button(root, text = "Manual", height=3, width=6)
roi_button_2 = Button(root, text = "AI", height=3, width=6)

fit_label = Label(root, text = "Lorentzian Fitting", height=3, width=12)
fit_button_1 = Button(root, text = "2-step", height=3, width=6)
fit_button_2 = Button(root, text = "AI", height=3, width=6)

calc_button = Button(root, text = "Calculate Concentrations", height=6)

load_button.grid(row=0, column=0, columnspan=2, pady=5)
correction_button.grid(row=1, column=0, columnspan=2, pady=5)
roi_label.grid(row=2, column=0, columnspan=2, pady=5)
roi_button_1.grid(row=3, column=0)
roi_button_2.grid(row=3, column=1)
fit_label.grid(row=4, column=0, columnspan=2, pady=5)
fit_button_1.grid(row=5, column=0)
fit_button_2.grid(row=5, column=1)
calc_button.grid(row=6, column=0, columnspan=2, pady=5)

root.mainloop()

    


    
