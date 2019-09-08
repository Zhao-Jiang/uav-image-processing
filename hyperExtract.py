# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:11:37 2019

Extracting average reflectancefor headwall-nano hyperspectral image.
arcpy and pandas needed (pandas.Dataframe.to_excel() can be replaced with numpy.savetxt())

@author: jiangzhao
"""

import arcpy
from arcpy.sa import *
from arcpy import env
import os

"""4 parameters"""
rst = r'Z:\Rape_temporal\0424\6304.tif'
ROI = r'Z:\Rape_temporal\BUFFER\buffer6304\XiaoNei.shp'
ROI_num = 24
env.workspace = r'Z:\Rape_temporal\results\analysis\0424hyper6304'

os.mkdir(env.workspace)

for band in range(1,272+1):
    band_temp=rst+'\\Band_'+str(band)
    print band_temp
    ZonalStatisticsAsTable(ROI, "BianHao", band_temp, str(env.workspace)+'\\'+str(band)+'.dbf', "DATA", "ALL")

import pandas as pd
def dbfAssemble(dbfList=[]):
    df=pd.DataFrame()
    nCol=0
    for table in dbfList:
        print table
        col_temp = range(ROI_num)
        cursor = arcpy.da.SearchCursor(table, "MEAN")
        nRow=0
        for row in cursor:
            col_temp[nRow] = row[0]
            nRow += 1
        colName = 'b_' + table[:-4] # band number ('b_125')
        df.insert(nCol,colName,col_temp)
        nCol += 1
        
    #write mean_reflectance_in_plot results (ROI_num plots*125bands)
    writer = pd.ExcelWriter(str(env.workspace)+'\\hyper_mean_272bands.xlsx')
#    df.T.to_excel(writer) # 转置得到 272*ROI_num
    df.to_excel(writer) # 转置得到 272*ROI_num
    writer.save()
    writer.close()

#dbfList = arcpy.ListTables('*')
dbfList = range(272)
for band in range(1,272+1):
    dbfList[band-1] = env.workspace + '\\' + str(band) + '.dbf'
dbfAssemble(dbfList)
