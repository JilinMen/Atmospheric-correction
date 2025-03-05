# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 11:28:30 2024

@author: jmen
"""
import os
import shutil
import netCDF4 as nc
import subprocess
from datetime import datetime
from tqdm import tqdm
import sys
# add the path of acolite_launcher.py
sys.path.append('D:\\Acolite')
from launch_acolite import launch_acolite
from glob import glob
#--------------------------------------------------------
#parameters need to be changed
settings = r'H:\Satellite_processing_ERSL\settings.txt'  #setting file                                         
Input_path = r'C:\Users\jmen\Box\ERSL_FieldDatabase\LakeLanier\2024October8\SatelliteImage\L1'      #input path L1 data       
Output_path = r'C:\Users\jmen\Box\ERSL_FieldDatabase\LakeLanier\2024October8\SatelliteImage\L2_acolite' #output path        
acolitepath = r'D:\acolite_py_win_20231023\acolite_py_win\dist\acolite\acolite.exe' #acolite.exe path
satellite = 'landsat-8&9' #landsat-8&9 or Sentinel-2
#--------------------------------------------------------

#read setting file
with open(settings,'r') as ef:
    examplecon=ef.read().split('\n')

fileList=os.listdir(Input_path)
settingList=[]    #setting path for each image

for f in fileList:
    if satellite == 'Sentinel-2':
        inputfile=os.path.join(Input_path,f)
        outputDir = os.path.join(Output_path,f.replace('L1C','L2'))
    elif satellite == 'landsat-8&9':
        inputfile=os.path.join(Input_path,f)
        outputDir = os.path.join(Output_path,f.replace('L1','L2'))
    
    if os.path.exists(outputDir):
        print("The output folder exists")
    else:
        print("The folder doest exist, has been created!")
        os.mkdir(outputDir)
    
    examplecon[1] = '## Written at ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    examplecon[2] = 'inputfile='+inputfile    #input path
    examplecon[3] = 'output='+outputDir       #output path
    settingFile = os.path.join(outputDir,f.split('.')[0]+'_setting.txt')  #update settings
    settingList.append(settingFile)

    with open(settingFile,'w') as outsetting:
        for ec in examplecon:
            outsetting.write(ec+'\n')          #write new settings
    
for stl in tqdm(settingList):              # loop setting
    with open(stl,'r') as ef:
        stl_ = ef.read().split('\n')
    
    if glob(os.path.join(stl_[3].split('=')[1],'*L2W.nc')) != []:
        print("This file has been processed, Skip")
    else:
        sys.argv = [
            acolitepath,
            '--cli',
            '--settings=' + stl
        ]
        
        # run Acolite
        launch_acolite()

