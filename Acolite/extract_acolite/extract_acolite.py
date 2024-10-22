"""
Requirements:
1. Clone the Acolite python library from https://github.com/acolite/acolite: git clone --depth 1 https://github.com/acolite/acolite
2. Install required libraries by Acolite:         conda install -c conda-forge numpy matplotlib scipy gdal pyproj scikit-image pyhdf pyresample netcdf4 h5py requests pygrib  cartopy
3. Install tqdm pandas
4. fill the parameter values in extract_acolite.json
5. provide a list of stations in stations.csv with id,lat,lon,date
6. provide a list of netcdf files in ncdfs.csv with file_path,date
7. run the script by python extract_acolite.py
8. joint the extract data back to stations using the ids
9. test data can be downloaded from https://lsu.box.com/s/tsj8eiqk4sjeiyra9e4p7pu1hdinqdkb
"""


import warnings
warnings.filterwarnings("ignore")
import sys, os, numpy as np
import json
import pandas as pd
from datetime import timedelta
from tqdm import tqdm


base_name, _ = os.path.splitext(__file__)
launch_json = base_name + '.json'
json_file_path = launch_json    
with open(json_file_path, 'r') as file:
    args = json.load(file)
    path = args["acolite"]
# add the acolite path to the environment
sys.path.append(path)
import acolite as ac



def main():
    # read parameters from the launch.json
    base_name, _ = os.path.splitext(__file__)
    launch_json = base_name + '.json'
    json_file_path = launch_json    
    with open(json_file_path, 'r') as file:
        args = json.load(file)
        ncf =  args["netcdfs"]
        stations = args["stations"]
        buffer = args["buffer"]

    # read the ncf file list from .csv
    ncfs_df = pd.read_csv(ncf)
    

    # read the station list from .csv
    stations_df = pd.read_csv(stations)
    # from each station, find a matching ncf file with time (location is not used for this step)
    # Convert 'date' columns to datetime
    stations_df['date'] = pd.to_datetime(stations_df['date'])
    ncfs_df['date'] = pd.to_datetime(ncfs_df['date'])

    # Create an empty DataFrame to store the results
    matches = []

    # Iterate over each row in stations_df
    for _, station_row in stations_df.iterrows():
        # Filter ncfs_df to get rows where the date difference is within 2 days
        ncfs_filtered = ncfs_df[(ncfs_df['date'] >= station_row['date'] - timedelta(days=2)) & 
                                (ncfs_df['date'] <= station_row['date'] + timedelta(days=2))]
        
        # If there are matching rows, store the results
        for _, ncfs_row in ncfs_filtered.iterrows():
            matches.append({
                'id': station_row['id'],
                'lat': station_row['lat'],
                'lon': station_row['lon'],
                'station_date': station_row['date'],
                'file': ncfs_row['file_path'],
                'ncfs_date': ncfs_row['date']
            })

    # Create a DataFrame from the matches
    result_df = pd.DataFrame(matches)
    compiled_data = []
    print(f"Extracting satellite data with a buffer size: {buffer}")
    for _, result_row in tqdm(result_df.iterrows()):
        extracted_data = ac.shared.nc_extract_point(result_row['file'], result_row["lon"], result_row["lat"], extract_datasets=None, shift_edge=False, box_size=buffer)
        if isinstance(extracted_data, dict):
            df = extracted_data['data']
            
            # Process to ensure a single value per key
            processed_data = {}
            processed_data['id'] = result_row['id']
            for key, values in df.items():
                processed_value = np.mean(values) 
                processed_data[key] = processed_value

            compiled_data.append(processed_data)

    # Display the result DataFrame
    df = pd.DataFrame(compiled_data)
    df.to_csv('satellite_data.csv', index=False)

    return

if __name__ == "__main__":
    main()
    
    
