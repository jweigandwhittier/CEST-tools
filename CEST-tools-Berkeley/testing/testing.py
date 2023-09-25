#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 15:35:05 2023

@author: jonah
"""
import numpy as np
import matplotlib.pyplot as plt

masked_cest = np.load('cest_masks.npy')
masked_cest = masked_cest[:,:,:,0,0]

plt.imshow(masked_cest[:,:,1])
