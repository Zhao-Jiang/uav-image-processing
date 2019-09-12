#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 20:51:33 2019

before using this script, check if:
    1. the nodata value of img is read as 255, and the nodata value of the label is read as 3
    2. background value of the label is 0
    3. foreground value of the label is 1

output label:
    background value of the .jpg label tile is 0
    foreground value of the .jpg label tile is 255

@author: jz
"""

import os
import numpy as np
from osgeo import gdal
import glob
import cv2

nodata_img = 255
nodata_label = 3
label_background = 0
label_foreground = 1

def imgPre(imgRaster, labelRaster, tileSize=(256,256), stride=64, saveTiles=True):   
    imgTif = gdal.Open(imgRaster)
    labelTif = gdal.Open(labelRaster)
    if saveTiles:
        (filepath, fullname) = os.path.split(imgRaster)
        (prename, suffix) = os.path.splitext(fullname)
        imgs_path = filepath + '/imgs'
        labels_path = filepath + '/labels'
        os.mkdir(imgs_path)
        os.mkdir(labels_path)
    else:
        print("Loading data as tiles from the whole tif image without saving.")
    if imgTif is None:
        print('Could not open the file ' + imgTif)
    else:
        tile_rows = int((imgTif.RasterYSize-tileSize[0]+stride)/stride)
        tile_cols = int((imgTif.RasterXSize-tileSize[1]+stride)/stride)
        
        imgArray = imgTif.ReadAsArray().swapaxes(0,1).swapaxes(1,2)
#        labelArray = (labelTif.ReadAsArray()/labelArray.max()).astype(np.uint8)
        labelArray = labelTif.ReadAsArray()
        
        # deal with nodata value
        imgArray[imgArray==nodata_img] = 0
        labelArray[labelArray==nodata_label] = 0
        
        # saved value of the label
        labelArray[labelArray==label_background] = 0
        labelArray[labelArray==label_foreground] = 255
        
        imgs = []
        labels = []
        for i in range(tile_rows):
            for j in range(tile_cols):
                img_temp = imgArray[i*stride:i*stride+tileSize[0], j*stride:j*stride+tileSize[1],:]
                label_temp = labelArray[i*stride:i*stride+tileSize[0], j*stride:j*stride+tileSize[1]]
                if img_temp.min() != img_temp.max() & label_temp.min() != label_temp.max(): # Tile not blank and TileLabel not blank
                    imgs.append(img_temp)
                    labels.append(label_temp)
                    if saveTiles:
                        cv2.imwrite(imgs_path+'/t_'+str(i)+'_'+str(j)+'.jpg', img_temp)
                        cv2.imwrite(labels_path+'/t_'+str(i)+'_'+str(j)+'.jpg', label_temp)
                    else:
                        continue
                else:
                    continue
        
        X = np.array(imgs)/255.0
        Y = np.array(labels)/255
        return (X, Y)
    
# loading tiles and saving tiles as a dataset
(X, Y) = imgPre(
        imgRaster='./wholeTifData/img.tif', 
        labelRaster='./wholeTifData/label.tif', 
        tileSize=(256,256), 
        stride=64, 
        saveTiles=True)
# loading tiles for training without saving
(X, Y) = imgPre(
        imgRaster='./wholeTifData/img.tif', 
        labelRaster='./wholeTifData/label.tif', 
        tileSize=(256,256), 
        stride=64, 
        saveTiles=False)
