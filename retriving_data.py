#python libraries
import etl as e
import argparse
import time
import os, sys
import pandas as pd
import geopandas as gpd
import datetime
from osgeo import gdal
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show

import pathlib
from create_report import content_report


# constant values

STATIC_DIR = "data/static"
PLOTS = "data/plots"
TEMP = "data/tifs"



#def querydata(config: dict, initial_date: str, final_date: str) -> pd.DataFrame:
def querydata(config: dict, initial_date: str, final_date: str) -> list:

    """ This function retrieves the data from database to do the interpolation operations
    Args:
        config:(str) the python dictionary which has the connection parameters to the databse
        initial_date: (str) the first date 
        final_date: (str) the final date 

    Returns:
        list: The list of two pandas dataframes 
    """
    #Query for interpolation maps
    query = f'''select id_sensor, avg(temp_value) as temp,  avg(noise_value) as noise, avg(hum_value) as humidity 
                from us.env_variables 
                where date >= {initial_date} and date <= {final_date}
                group by id_sensor'''
    #query for time series graph
    query_ts = f'''select date, avg(temp_value) as temp,  avg(noise_value) as noise, avg(hum_value) as humidity 
                from us.env_variables 
                where date >= {initial_date} and date <= {final_date}
                group by date'''
    
    try:
        connection = e.DBController(**config["database"])
        
        query_df = connection.select_data(query)

        query_ts_df = connection.select_data(query_ts)
    # Encapsulate both pandas dataframe into a list
        list_querys_df = [query_df, query_ts_df]

        if (query_df.shape[0] or query_ts_df.shape[0]) == 0:

            e.done("CHOOSE OTHER DATES INTERVAL, THERE ARE NOT DATA FOR YOUR DATES")    
        
    except Exception as err:
        
        e.die(f"error in query data: {e}")
    
    return list_querys_df


def sum_variables(config: dict, filtered_df_list) -> list:
    """ This function summarize the values for each environmental variable
    Args:
        config:(str) the python dictionary which has the path to sensors geojson 
        filtered_df_list: (list) The list with two pandas dataframe which were created by query data function 

    Returns:
        list: The list of three  geodataframes, each one for each environmental variable
        pd.dataframe: pandas Dataframe with values for time series graphics
    """
# Split the list to get each dataframe

    filtered_df = filtered_df_list[0]
    filtered_df_ts = filtered_df_list[1]

# Removing null values and creating new 3 dataframes

    temp = filtered_df[['id_sensor','temp']].dropna()

    noise = filtered_df[['id_sensor','noise']].dropna()

    humidity = filtered_df[['id_sensor','humidity']].dropna()

# creating geodaframes merged with pandas dataframe values 

    sensors = config["fname_stations"]
    gdf_sensors = e.read_geojson(f"{STATIC_DIR}/{sensors}")

    gdf_sensors = gdf_sensors.to_crs(epsg=4326)
        
    geo_temp = gdf_sensors.merge(temp, on = 'id_sensor')
  
    geo_temp = geo_temp[['id_sensor', 'lat', 'long', 'geometry', 'temp']]

    geo_noise = gdf_sensors.merge(noise, on = 'id_sensor')
    
    geo_noise = geo_noise[['id_sensor', 'lat', 'long', 'geometry', 'noise']]

    geo_hum = gdf_sensors.merge(humidity, on = 'id_sensor')
    
    geo_hum = geo_hum[['id_sensor', 'lat', 'long', 'geometry', 'humidity']]

    # Three geodataframes into a list

    list_geogdf = [geo_temp, geo_noise, geo_hum]

    return list_geogdf, filtered_df_ts

def interpolation(list_geo):

    """ This function creates raster files for each environmental variable
    Args:
        list_geo:(str) the list with the three geodataframes obtained from sum_variables function 

    Returns:
        None
    """

    #constants for this function
    i = 0
    # bounds for the raster files in geograhic coordinates
    bounds = [-9.24, 38.8, -9.08, 38.68]

    # iteration over each geodataframe to create the tif file
    for m in list_geo:

        i = i+1
        filename = (str(i) + '.tif')
        file = pathlib.Path(f"{TEMP}/{filename}")
        if file.exists():
            os.remove(file) 
    
        zvalue = m.columns[-1]

    # operation for setting pixel size close to 10 meters


        pixel_size = 10

        width = round((bounds[2] - bounds[0])/pixel_size)
        height = round((bounds[3] - bounds[1])/pixel_size)

        
    # convert the geodataframe to specific array of values that gdal uses for IDW operation

        input = gdal.OpenEx(m.to_json(), gdal.OF_VECTOR)
    # Interpolation and saving the tif files 
        IDW_gdal = gdal.Grid(f"{TEMP}/{filename}", input, format="GTiff", width=width, height=height, outputBounds=bounds, algorithm="invdist", zfield=zvalue)


def plots(list_geo, filtered_df_ts:pd.DataFrame):

    """ This function creates the neccesary plots for the report
    Args:
        list_geo:(str) the list with the three geodataframes obtained from sum_variables function
        filtered_df_ts: a dataframe with the values to create time series graphics 

    Returns:
        None
    """    
    # reading fraguesias geojson

    gdf_lisbon = e.read_geojson(f"{STATIC_DIR}/fraguesias.geojson")

    gdf_lisbon = gdf_lisbon.to_crs(epsg=4326)

    # removing files from the folder in case previous files exist there
    if len(os.listdir(PLOTS)) > 0:
        
        for f in os.listdir(PLOTS):

            file_path = os.path.join(PLOTS, f)
            try:
                os.remove(file_path)
            except:
                pass
    
    # Temperature plot for report using subplots on the same axes

    r_temp = rasterio.open(f"{TEMP}/1.tif")
    p_temp = list_geo[0]
     
    fig_t, ax_t = plt.subplots(1, figsize=(8, 5))
    show((r_temp, 1), cmap='viridis', interpolation='none', ax=ax_t)
    show((r_temp, 1), contour=True, ax=ax_t)
    gdf_lisbon.boundary.plot(ax=ax_t, zorder=1, edgecolor='black')
    p_temp.plot(column='temp', ax=ax_t, legend=True, legend_kwds={'label': 'Degrees Celsius', 'orientation': "vertical"}, zorder=2)
    p_temp.plot(ax = ax_t, color = 'black', marker='h', markersize=20, zorder=3)
    #removing grids
    ax_t.set_axis_off()
    #saving the png file 
    fig_t.savefig(f'{PLOTS}/temperature.png')

    # Noise plot for report

    r_noise = rasterio.open(f"{TEMP}/2.tif")
    p_noise = list_geo[1]
     
    fig_n, ax_n = plt.subplots(1, figsize=(8, 5))
    show((r_noise, 1), cmap='viridis', interpolation='none', ax=ax_n)
    show((r_noise, 1), contour=True, ax=ax_n)
    gdf_lisbon.boundary.plot(ax=ax_n, zorder=1, edgecolor='black')
    p_noise.plot(column='noise', ax=ax_n, legend=True, legend_kwds={'label': 'Decibels', 'orientation': "vertical"}, zorder=2)
    p_noise.plot(ax = ax_n, color = 'black', marker='h', markersize=20, zorder=3)

    ax_n.set_axis_off()
    
    fig_n.savefig(f'{PLOTS}/noise.png')
        
    # Humidity plot for report

    r_hum = rasterio.open(f"{TEMP}/3.tif")
    p_hum = list_geo[2]
     
    fig_h, ax_h = plt.subplots(1, figsize=(8, 5))
    show((r_hum, 1), cmap='viridis', interpolation='none', ax=ax_h)
    show((r_hum, 1), contour=True, ax=ax_h)
    gdf_lisbon.boundary.plot(ax=ax_h, zorder=1, edgecolor='black')
    p_hum.plot(column='humidity', ax=ax_h, legend=True, legend_kwds={'label': 'Humidity Percentage', 'orientation': "vertical"}, zorder=2)
    p_hum.plot(ax = ax_h, color = 'black', marker='h', markersize=20, zorder=3)
    
    ax_h.set_axis_off()
    
    fig_h.savefig(f'{PLOTS}/humidity.png')

    # Average temperature value per date in Lisbon

    filtered_df_ts["date"] = pd.to_datetime(filtered_df_ts["date"])
    
    fig_t_date, ax_td = plt.subplots(figsize=(10, 4))
    filtered_df_ts.groupby(filtered_df_ts['date'].dt.hour)["temp"].plot(kind='bar', rot=0, ax=ax_td)
    plt.xlabel("day");
    plt.ylabel("Lisbon average temperature")

    fig_t_date.savefig(f'{PLOTS}/temp_ts.png')

    # Average noise value per date in Lisbon

    filtered_df_ts["date"] = pd.to_datetime(filtered_df_ts["date"])

    fig_n_date, ax_nd = plt.subplots(figsize=(10, 4))
    filtered_df_ts.groupby(filtered_df_ts['date'].dt.hour)["noise"].plot(kind='bar', rot=0, ax=ax_nd)
    plt.xlabel("day");
    plt.ylabel("Lisbon average noise")

    fig_n_date.savefig(f'{PLOTS}/noise_ts.png')

    # average humidity value per date in Lisbon
    
    filtered_df_ts["date"] = pd.to_datetime(filtered_df_ts["date"])

    fig_h_date, ax_hd = plt.subplots(figsize=(10, 4))
    filtered_df_ts.groupby(filtered_df_ts['date'].dt.hour)["humidity"].plot(kind='bar', rot=0, ax=ax_hd)
    plt.xlabel("day");
    plt.ylabel("Lisbon average temperature")

    fig_h_date.savefig(f'{PLOTS}/hum_ts.png')


def main(config_file: str, initial_date:str, final_date:str) -> None:

    """The main function for Query data, summarize data, create raster files and plots.

    Args:
        config_file (str): configuration file
        initial_date (str): the initial date for querying data using this format: yyyy-mm-dd
        final_date (str): the final date for querying data using this format: yyyy-mm-dd
    """
    t0= time.time()
    config = e.read_config(config_file)
    

    e.info("EXECUTING QUERY FOR SELECTED DATES")

    filtered_df_list = querydata(config, initial_date, final_date)
    t1= time.time()
    e.info("QUERY OPERATION TIME FOR REPORT: " + str(t1-t0)+ " seconds")
    
    e.info("SUMMARIZING ENV VARIABLES FOR MAPS")

    list_geo, filtered_df_ts = sum_variables(config, filtered_df_list)
    t2 = time.time()
    e.info("SUMMARIZING OPERATION TIME FOR REPORT: " + str(t2-t1)+ " seconds")
    
    e.info("CREATING RASTER FILES OF INTERPOLATION")

    interpolation(list_geo)

    t3 = time.time()
    e.info("INTERPOLATION OPERATION TIME FOR REPORT: " + str(t3-t2)+ " seconds")

    e.info("PLOTING ENV VARIABLE MAPS")

    plots(list_geo, filtered_df_ts)

    t4 = time.time()
    e.info("PLOTTING OPERATION TIME FOR REPORT: " + str(t4-t3)+ " seconds")

    e.info("CREATING PDF FILE")

    pdfname = config["fname_report"]

    content_report(pdfname, initial_date, final_date)

    t5 = time.time()
    e.info("TIME CREATING PDF FILE: " + str(t5-t4)+ " seconds")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Enviromental Maps for Lisbon')
    parser.add_argument("--config_file", required=False, help="The configuration file",default="./config/00.yml")
    parser.add_argument('--initial_date',required=False, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), help="indicate the initial date, e.g.:2022-02-20")       
    parser.add_argument('--final_date',required=False, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), help="indicate the final date, e.g.:2022-02-20")
    
    
    args = parser.parse_args()
    # In case user does not put arguments
    config_file = "./config/00.yml" if not args.config_file else args.config_file
    initial_date = "'2022-02-01'" if not args.initial_date else args.initial_date
    final_date = "'2022-02-20'" if not args.final_date else args.final_date

    main(config_file, initial_date, final_date)
