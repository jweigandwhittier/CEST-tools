#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 13:08:57 2023

@author: JWW
"""
import numpy as np

def b1_mapping(angles, cest_zspecs):
    angle_60 = angles[0]
    angle_120 = angles[1]
    b1_map = np.nan_to_num(np.arccos(angle_120/(2*angle_60)))
    ##Double resolution of undersized image##
    if np.size(b1_map, 0) == 0.5*np.size(cest_zspecs, 0):
       b1_map = np.repeat(b1_map, 2, axis = 0)
       b1_map = np.repeat(b1_map, 2, axis = 1)
    return b1_map