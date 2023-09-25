#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 13:08:57 2023

@author: JWW
"""
import numpy as np

def b1_mapping(angles, cest_zspecs):
    # if np.size(angles, axis=0) == 0.5*np.size(cest_zspecs):
    angle_60 = angles[0]
    angle_120 = angles[1]
    b1_map = np.arccos(angle_120/(2*angle_60))
    return b1_map