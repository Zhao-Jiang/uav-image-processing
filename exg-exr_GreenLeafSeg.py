#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 09:51:18 2019

Calculating exg-exr and do the segmentation of green leave.
gdal(python3) needed

@author: jz
"""


import os
import numpy as np
from osgeo import gdal
import glob
import argparse

parser = argparse.ArgumentParser(
    description='Script to run ExG-ExR segmentation ')
parser.add_argument("--dataDir", help="path to orthomosaic dir")
args = parser.parse_args()
dataDir = args.data + '/'

# dataDir = '/media/jz/Elements/2018_Rice/RGB/daPeng/'
list_tif = glob.glob(dataDir+'*.tif')
out_path = dataDir + 'result/'
os.mkdir(out_path)

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
        
        Nb=b/(b+g+r)
        Ng=g/(b+g+r)
        Nr=r/(b+g+r)
        
#        ExG=Ng*2-Nr-Nb
#        ExR=Nr*1.4-Ng
        ExG_ExR = (Ng*2 - Nr - Nb) - (Nr*1.4 - Ng) # =Ng*3 - Nr*2.4 - Nb
        
        ExG_ExR_binary = np.zeros(ExG_ExR.shape).astype(np.uint8)
        ExG_ExR_binary[ExG_ExR<0] = 0
        ExG_ExR_binary[ExG_ExR>=0] = 1
        
        ExG_ExR_masked = ExG_ExR
        ExG_ExR_masked[ExG_ExR_binary==0] = 0
        
        ##1 将计算好的VI保存为GeoTiff文件
        gtiff_driver = gdal.GetDriverByName('GTiff')
        # 批量处理需要注意文件名是变量，这里截取对应原始文件的不带后缀的文件名
        out_ds = gtiff_driver.Create(out_path + prename + '_ExG-ExR.tif',
                         ExG_ExR.shape[1], ExG_ExR.shape[0], 1, gdal.GDT_Float32)
        # 将NDVI数据坐标投影设置为原始坐标投影
        out_ds.SetProjection(in_ds.GetProjection())
        out_ds.SetGeoTransform(in_ds.GetGeoTransform())
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(ExG_ExR)
        out_band.FlushCache()
        
        ##2 将计算好的binary保存为GeoTiff文件
        gtiff_driver = gdal.GetDriverByName('GTiff')
        # 批量处理需要注意文件名是变量，这里截取对应原始文件的不带后缀的文件名
        out_ds = gtiff_driver.Create(out_path + prename + '_ExG-ExR_binary.tif',
                         ExG_ExR_binary.shape[1], ExG_ExR_binary.shape[0], 1, gdal.GDT_Float32)
        # 将NDVI数据坐标投影设置为原始坐标投影
        out_ds.SetProjection(in_ds.GetProjection())
        out_ds.SetGeoTransform(in_ds.GetGeoTransform())
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(ExG_ExR_binary)
        out_band.FlushCache()
        
        ##3 将计算好的masked vi保存为GeoTiff文件
        gtiff_driver = gdal.GetDriverByName('GTiff')
        # 批量处理需要注意文件名是变量，这里截取对应原始文件的不带后缀的文件名
        out_ds = gtiff_driver.Create(out_path + prename + '_ExG-ExR_masked.tif',
                         ExG_ExR_masked.shape[1], ExG_ExR_masked.shape[0], 1, gdal.GDT_Float32)
        # 将NDVI数据坐标投影设置为原始坐标投影
        out_ds.SetProjection(in_ds.GetProjection())
        out_ds.SetGeoTransform(in_ds.GetGeoTransform())
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(ExG_ExR_masked)
        out_band.FlushCache()
