#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 10:04:19 2024

@author: willy

geo visualization with geojson and Polygon
"""
import os
import json
import pyproj
import folium
import geojson
import pandas as pd
import numpy as np
from pathlib import Path

###############################################################################
#                           constante: start
############################################################################### 
# Spatial Reference System
inputEPSG = 32630 # 32629 #3857
outputEPSG = 4326

rootdata = "./data"
rootdata_geo = "./data_geojson"
rootdata_html = "./html_visu"
###############################################################################
#                           constante: end
############################################################################### 

def visu_geojson_polygon():
    rootpath = "./data_geojson/"
    filename = "Kuntarajat_aluevesirajoilla_2017.geojson"
    fo_m = folium.Map([30.5, -97.5], zoom_start=10)
    folium.GeoJson(os.path.join(rootpath, filename),
                   tooltip=folium.GeoJsonTooltip(fields=['description', 'Name'])
                   ).add_to(fo_m)
    
    html_directory = "html_visu"
    Path(html_directory).mkdir(parents=True, exist_ok=True)
    path_name = os.path.join(html_directory, f"{filename}_folium_geojson.html")
    fo_m.save(path_name)
    
###############################################################################
#               compute latitude longitude coordinates: start
############################################################################### 
def convert_XY_to_latlon(X1):
    proj = pyproj.Transformer.from_crs(inputEPSG, outputEPSG, always_xy=True)
    X1_lat, X1_lon = proj.transform(X1[0], X1[1])
    return X1_lat, X1_lon
   
def compute_geostat_coordinate(df):
    for name, coord in df.index:
        X = df.loc[(name,coord),"X"]
        Y = df.loc[(name,coord),"Y"]
        lat, lon =  convert_XY_to_latlon((X,Y))
        df.loc[(name,coord),"Lat"] = lat
        df.loc[(name,coord),"Lon"] = lon
    
    return df
###############################################################################
#               compute latitude longitude coordinates: end
############################################################################### 
def get_geosjon_properties_coordinates(name_df, name_parcelle, area, perim):
    properties = dict()
    coordinates = list()
    
    description = '<div class=\"googft-info-window\">\n'
    debut_balise = "<ul>\n"
    
    coords = list(name_df.index)
    for i, coord in enumerate(coords):
        lat = name_df.loc[coord,"Lat"]
        lon = name_df.loc[coord,"Lon"]
        properties[f"{coord}_lat"] = [lat]
        properties[f"{coord}_lon"] = [lon]
        properties["name_parcelle"] = name_parcelle
        properties["area"] = round(area, 4)
        properties["perim"] = round(perim, 4)
        coordinates.append([lat, lon])
        
        
        r_lat = round(lat, 4)
        r_lon = round(lon, 4)
        tmp = f"<li> X{i} = {r_lat, r_lon} </li> \n"
        debut_balise += tmp
        
    debut_balise += "</ul>"
    description = description + debut_balise +"</div>"
    properties["description"] = description
    
    coordinates.append(coordinates[0])
        
    return coordinates, properties
    

def turn_file_from_csv_to_geojson(csv_filename, geojson_filename):

    data_csv = os.path.join( rootdata, csv_filename)
    
    df = pd.read_csv(data_csv, index_col=[0,1], sep=";", header=1)
    df = pd.read_csv(data_csv, sep=";", header=1)
    df = df.ffill()
    
    df.set_index(['Name', 'Coord'], inplace=True)
    
    df = compute_geostat_coordinate(df)
    
    #index_names = df.index.names # ---> get the name of index columns
    names = df.index.get_level_values(level=0)
    names = set(names)
    
    features = list()
    for name_parcelle in names:
        name_df = df.loc[(name_parcelle,),]
        lats = np.array(name_df.loc[:,"Lat"])
        lons = np.array(name_df.loc[:,"Lon"])
        # Define WGS84 as CRS:
        geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')
        # Compute:
        area, perim = geod.polygon_area_perimeter(lons, lats)
        
        coordinates, properties \
            = get_geosjon_properties_coordinates(name_df, name_parcelle, area, perim)
        
        
        feature = {"type": "Feature", "properties": properties,
                   "geometry": {"type": "LineString", "coordinates": coordinates}}
                   #"geometry": {"type": "Polygon", "coordinates": coordinates}}
        
        features.append(feature)
        
    geojson_dico = {"type": "FeatureCollection",
                    "crs": { "type": "name", 
                            "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } 
                            },
                    "features": features}
    
    
    path_filename = os.path.join(rootdata_geo, geojson_filename)
    with open(path_filename,'w') as f:
        json.dump(geojson_dico, f)
    
    return path_filename

###############################################################################
#               test geojson functions : start
###############################################################################
def turn_file_from_csv_to_geojson_NEW(csv_filename, geojson_filename):

    data_csv = os.path.join( rootdata, csv_filename)
    
    df = pd.read_csv(data_csv, index_col=[0,1], sep=";", header=1)
    df = pd.read_csv(data_csv, sep=";", header=1)
    df = df.ffill()
    
    df.set_index(['Name', 'Coord'], inplace=True)
    
    df = compute_geostat_coordinate(df)
    
    #index_names = df.index.names # ---> get the name of index columns
    names = df.index.get_level_values(level=0)
    names = set(names)
    
    features = list()
    for name_parcelle in names:
        name_df = df.loc[(name_parcelle,),]
        lats = np.array(name_df.loc[:,"Lat"])
        lons = np.array(name_df.loc[:,"Lon"])
        # Define WGS84 as CRS:
        geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')
        # Compute:
        area, perim = geod.polygon_area_perimeter(lons, lats)
        
        coordinates, properties \
            = get_geosjon_properties_coordinates(name_df, name_parcelle, area, perim)
        
        
        feature = {"type": "Feature", "properties": properties,
                   "geometry": {"type": "LineString", "coordinates": coordinates}}
                   #"geometry": {"type": "Polygon", "coordinates": coordinates}}
        
        features.append(feature)
        
    #geom_in_geojson = geojson.Feature(geometry=features, properties={})
    geojson_dico = geojson.FeatureCollection(features=features)
    # geojson_dico = {"type": "FeatureCollection",
    #                 "crs": { "type": "name", 
    #                         "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } 
    #                         },
    #                 "features": features}
    
    
    path_filename = os.path.join(rootdata_geo, geojson_filename)
    with open(path_filename,'w') as f:
        json.dump(geojson_dico, f)
    
    return path_filename
###############################################################################
#               test geojson functions : end
###############################################################################

def visu_geojson_polygon_assouinde(filename):
    fo_m = folium.Map(location=[5.2779,-3.8764], zoom_start=10)
    # fl_n = folium.Map(location=[5.2779,-3.8764], 
    #                     tiles="OpenStreetMap", 
    #                     zoom_start=10)
    folium.GeoJson(os.path.join(rootdata_geo, f"{filename}.geojson"),
                   tooltip=folium.GeoJsonTooltip(fields=['name_parcelle', 
                                                         'perim', 'area',
                                                         'description'])
                   ).add_to(fo_m)
    
    html_directory = "html_visu"
    Path(html_directory).mkdir(parents=True, exist_ok=True)
    
    path_name = os.path.join(html_directory, f"{filename}_folium_geojson.html")
    fo_m.save(path_name)
    
        
    
    
if __name__ == "__main__":
    visu_geojson_polygon()
    filename = "assouande42parcelles"
    csv_filename = filename+".csv" # assouande42parcelles.csv
    geojson_filename = filename+".geojson" # assouande42parcelles.geojson
    
    #path_filename = turn_file_from_csv_to_geojson(csv_filename, geojson_filename)
    
    #visu_geojson_polygon_assouinde(filename)
    
    
    path_filename = turn_file_from_csv_to_geojson_NEW(csv_filename, geojson_filename)
    
    visu_geojson_polygon_assouinde(filename)
    