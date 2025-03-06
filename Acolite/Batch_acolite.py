# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 11:28:30 2024

run acolite with multiprocess
@author: jmen
"""
import os
import sys
import shutil
import netCDF4 as nc
import subprocess
from datetime import datetime
from tqdm import tqdm
from glob import glob
from multiprocessing import Pool, cpu_count

# --------------------------------------------------------
# Parameters Configuration
sys.path.append('D:\\Acolite')  # Path of acolite_launcher.py
from launch_acolite import launch_acolite

settings = r'H:\Satellite_processing_ERSL\settings_1.txt'  # Settings file
Input_path = r'H:\Satellite_processing_ERSL\L1\S2'  # Input L1 data path
Output_path = r'H:\Satellite_processing_ERSL\L1\test_output'  # Output path
acolitepath = r'D:\acolite_py_win_20231023\acolite_py_win\dist\acolite\acolite.exe'  # Acolite executable path
satellite = 'Sentinel-2'  # Choices: 'landsat-8&9' or 'Sentinel-2'
num_processes = min(4, cpu_count())  # Number of CPU cores to use (max 4)
# --------------------------------------------------------

# Read base settings
with open(settings, 'r') as ef:
    examplecon = ef.read().split('\n')

fileList = os.listdir(Input_path)
settingList = []

# Prepare settings files for each image
for f in fileList:
    if satellite == 'Sentinel-2':
        inputfile = os.path.join(Input_path, f, f)
        outputDir = os.path.join(Output_path, f.replace('L1C', 'L2'))
    elif satellite == 'landsat-8&9':
        inputfile = os.path.join(Input_path, f)
        outputDir = os.path.join(Output_path, f.replace('L1', 'L2'))
    else:
        raise ValueError("Unsupported satellite type. Choose 'Sentinel-2' or 'landsat-8&9'.")

    # Create output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)

    # Update settings
    examplecon[1] = '## Written at ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    examplecon[2] = f'inputfile={inputfile}'
    examplecon[3] = f'output={outputDir}'

    settingFile = os.path.join(outputDir, f.split('.')[0] + '_setting.txt')
    settingList.append(settingFile)

    with open(settingFile, 'w') as outsetting:
        outsetting.write('\n'.join(examplecon) + '\n')

def process_acolite(setting_file):
    """ Run Acolite for each image """
    with open(setting_file, 'r') as ef:
        stl_ = ef.read().split('\n')

    if glob(os.path.join(stl_[3].split('=')[1], '*L2W.nc')):
        print(f"{setting_file} already processed, skipping.")
        return

    sys.argv = [acolitepath, '--cli', '--settings=' + setting_file]
    launch_acolite()


if __name__ == '__main__':
    print(f"Using {num_processes} CPU cores for parallel processing.")
    with Pool(processes=num_processes) as pool:
        list(tqdm(pool.imap_unordered(process_acolite, settingList), total=len(settingList)))

