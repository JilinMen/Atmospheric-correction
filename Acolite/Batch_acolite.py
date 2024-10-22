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
# 添加 acolite_launcher.py 所在的文件夹路径
sys.path.append('D:\\Acolite')
from launch_acolite import launch_acolite
from glob import glob
#--------------------------------------------------------
#需要修改的变量
settings = r'H:\Satellite_processing_ERSL\settings.txt'  #一个Setting文件例子                                            
Input_path = r'C:\Users\jmen\Box\ERSL_FieldDatabase\LakeLanier\2024October8\SatelliteImage\L1'      #input path L1 data       
Output_path = r'C:\Users\jmen\Box\ERSL_FieldDatabase\LakeLanier\2024October8\SatelliteImage\L2_acolite' #output path        
acolitepath = r'D:\acolite_py_win_20231023\acolite_py_win\dist\acolite\acolite.exe' #acolite.exe path
satellite = 'landsat-8&9' #landsat-8&9 or Sentinel-2
#--------------------------------------------------------

#读出例子Setting文件的内容
with open(settings,'r') as ef:
    examplecon=ef.read().split('\n')

fileList=os.listdir(Input_path)
settingList=[]    #存放各setting文件的路径

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
    examplecon[2] = 'inputfile='+inputfile    #修改输入的文件路径
    examplecon[3] = 'output='+outputDir       #修改输出的文件路径
    settingFile = os.path.join(outputDir,f.split('.')[0]+'_setting.txt')  #不断生成新的setting文件的文件名
    settingList.append(settingFile)

    with open(settingFile,'w') as outsetting:
        for ec in examplecon:
            outsetting.write(ec+'\n')          #生成新的setting文件
    
for stl in tqdm(settingList):              # 循环调用setting文件，进行批处理
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
        
        # 运行 Acolite
        launch_acolite()

