#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 09:51:18 2019

Calculating exg-exr and do the segmentation of green leave.

@author: jz
"""


import os
import numpy as np
from osgeo import gdal
import glob
import cv2
import argparse

parser = argparse.ArgumentParser(
    description='Script to run ExG-ExR segmentation ')
parser.add_argument("--dataDir", help="path to orthomosaic dir",default='./pot')
args = parser.parse_args()
dataDir = args.dataDir + '/'

list_tif = glob.glob(dataDir+'*jpg')
out_path = dataDir + 'result/'
try:
    os.mkdir(out_path)
except:
    pass

for tif in list_tif:
    in_ds = gdal.Open(tif)
    # 获取文件所在路径以及不带后缀的文件名
    (filepath, fullname) = os.path.split(tif)
    (prename, suffix) = os.path.splitext(fullname)
    if in_ds is None:
        print('Could not open the file ' + tif)
    else:
        # DN
        r = in_ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
        g = in_ds.GetRasterBand(2).ReadAsArray().astype(np.float32)
        b = in_ds.GetRasterBand(3).ReadAsArray().astype(np.float32)
        
        Lightness = np.sqrt((r**2+g**2+b**2)/3.0)

        Nb=b/(b+g+r)
        Ng=g/(b+g+r)
        Nr=r/(b+g+r)
        
        # ExG=Ng*2-Nr-Nb
        # ExR=Nr*1.4-Ng
        ExG_ExR = (Ng*2 - Nr - Nb) - (Nr*1.4 - Ng) # =Ng*3 - Nr*2.4 - Nb
        
        ExG_ExR_binary = np.zeros(ExG_ExR.shape).astype(np.uint8)
        # thresholds
        ExG_ExR_binary[ExG_ExR>=0] = 255
        ExG_ExR_binary[Lightness<np.mean(Lightness)] = 0

        # ExG_ExR_masked = ExG_ExR
        # ExG_ExR_masked[ExG_ExR_binary==0] = 0
        
        # cv2.imwrite(out_path + prename + '_ExG-ExR.jpg',ExG_ExR)
        cv2.imwrite(out_path + prename + '_ExG-ExR_binary.jpg',ExG_ExR_binary)
        # cv2.imwrite(out_path + prename + '_ExG-ExR_masked.jpg',ExG_ExR_masked)
        # cv2.imwrite(out_path + prename + '_Lightness.jpg',Lightness)
