#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 14:02:17 2023

@author: jonah
"""
from resources.load_2dseq import load_2dseq
import matplotlib.pyplot as plt

cest_paths = ['/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230911_122534_C57BL6J_F1_Test_1_4/5_CEST_5ppm_1uT', '/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230911_122534_C57BL6J_F1_Test_1_4/8_CEST_M0']
wassr_paths = ['/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230911_122534_C57BL6J_F1_Test_1_4/6_WASSR', '/Users/jonah/Documents/MRI_Data/Berkeley/Test/20230911_122534_C57BL6J_F1_Test_1_4/9_WASSR_M0']

m0_image, zspecs, ppm_list = load_2dseq(cest_paths)

    