#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 16:29:43 2024

@author: willy
"""

import os
import json

import pyproj
import scipy
import folium
import geojson # pip install geojson
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

# Spatial Reference System
inputEPSG = 32630 # 32629 #3857
outputEPSG = 4326

def convert_XY_to_latlon(X1):
    proj = pyproj.Transformer.from_crs(inputEPSG, outputEPSG, always_xy=True)
    X1_lat, X1_lon = proj.transform(X1[0], X1[1])
    return X1_lat, X1_lon

def read_csv(data_path="projet_geo_assouinde", nom_site="assouande3parcelles_test.csv"):
    #data_csv = os.path.join('/home/willy/Bureau/Python', data_path, "data", nom_site)
    data_csv = os.path.join( data_path, "data", nom_site)
    df = pd.read_csv(data_csv, index_col=[0,1], sep=";", header=1)
    df = pd.read_csv(data_csv, sep=";", header=1)
    df = df.ffill()
    
    df.set_index(['Name', 'Coord'], inplace=True)
    
    names = list()
    coords = list()
    for name, coord in df.index:
        X = df.loc[(name,coord),"X"]
        Y = df.loc[(name,coord),"Y"]
        lat, lon =  convert_XY_to_latlon((X,Y))
        df.loc[(name,coord),"Lat"] = lat
        df.loc[(name,coord),"Lon"] = lon
        names.append(name)
        coords.append(coord)
        
    names = list(set(names))
    
    
    # Make an empty map
    fl_n = folium.Map(location=[5.2779,-3.8764], 
                      tiles="OpenStreetMap", 
                      zoom_start=10)
    
    for name in names:
        data_df = df.loc[(name,),]
        lats = np.array(data_df.loc[:,"Lat"])
        lons = np.array(data_df.loc[:,"Lon"])
        # Define WGS84 as CRS:
        geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')
        # Compute:
        area, perim = geod.polygon_area_perimeter(lons, lats)
        
        dico = dict()
        coords = list(data_df.index)
        for coord in coords:
            dico[f"{coord}_lat"] = [data_df.loc[coord,"Lat"]]
            dico[f"{coord}_lon"] = [data_df.loc[coord,"Lon"]]
            dico["name"] = name
            dico["area"] = [area]
            dico["perim"] = [perim]
            
        data = pd.DataFrame.from_dict(dico)
        
        for i in range(0,len(data)):
            html=f"""
                <h1> {data.iloc[i]['name']}</h1>
                <p>infos de la parcelle </p>
                <ul>
                    <li>surface: {data.iloc[i]['area']}</li>
                    <li>Point 1: {data.iloc[i]['X1_lat'], data.iloc[i]['X1_lon']} </li>
                    <li>Point 2: {data.iloc[i]['X2_lat'], data.iloc[i]['X2_lon']} </li>
                    <li>Point 3: {data.iloc[i]['X3_lat'], data.iloc[i]['X3_lon']} </li>
                    <li>Point 4: {data.iloc[i]['X4_lat'], data.iloc[i]['X4_lon']} </li>
                </ul>
                </p>
                <p>And that's a <a href="https://python-graph-gallery.com">link</a></p>
                """
            iframe = folium.IFrame(html=html, width=200, height=200)
            
            popup = folium.Popup(iframe, max_width=2650)
            
            popup = folium.Popup(iframe, max_width=2650)
            folium.Marker(
                location=[data.iloc[i]['X1_lon'], data.iloc[i]['X1_lat']],
                popup=popup,
                icon=folium.DivIcon(html=f"""
                    <div><svg>
                        <circle cx="50" cy="50" r="40" fill="#69b3a2" opacity=".4"/>
                        <rect x="35", y="35" width="30" height="30", fill="red", opacity=".3"/>
                    </svg></div>""")
            ).add_to(fl_n)
                
    # Show the map again
    name_file = nom_site.split(".")[0]
    fl_n.save(f"visu_folium_{name_file}.html")
    
    pass

def add_lat_lon_to_dataframe(data_path="projet_geo_assouinde", 
                             nom_site="assouande3parcelles_test.csv"):
    data_csv = os.path.join( data_path, "data", nom_site)
    df = pd.read_csv(data_csv, index_col=[0,1], sep=";", header=1)
    df = pd.read_csv(data_csv, sep=";", header=1)
    df = df.ffill()
    
    df.set_index(['Name', 'Coord'], inplace=True)
    
    names = list()
    coords = list()
    for name, coord in df.index:
        X = df.loc[(name,coord),"X"]
        Y = df.loc[(name,coord),"Y"]
        lat, lon =  convert_XY_to_latlon((X,Y))
        df.loc[(name,coord),"Lat"] = lat
        df.loc[(name,coord),"Lon"] = lon
        names.append(name)
        coords.append(coord)
        
    return df, names, coords

def creation_geojson_file(data_path="projet_geo_assouinde", 
                          nom_site="assouande3parcelles_test.csv",
                          data_geo_save="data_geojson"):
    
    df, names, coords = add_lat_lon_to_dataframe(data_path, nom_site)
    """
    liste_coords = [[-3.8759994466211367,5.278300354992908],
                    [-3.875881343998543,5.278440244239576],
                    [-3.8757756231030953,5.278360104301768],
                    [-3.87590163941897,5.278211640433852],
                    [-3.8759994466211367,5.278300354992908]]
    id_x = "0"
    name_parcelle = "Parcelle"
    source_geojson = f'{"type":"FeatureCollection", "features":[{"type":"Feature","properties":"{}",
                        "name":{name_parcelle},
                        "geometry":{"coordinates":{liste_coords},"type":"LineString"},"id":{id_x}}]}'
                    
    a1 = '{"type":"FeatureCollection", "features":[{"type":"Feature","properties":"{}",'
    a2 = f'"name":{name_parcelle},'
    c1 = f'"coordinates":{liste_coords},"type":"LineString"'
    g1 = '"geometry":{'+c1+'},'
    i1 = "id:{"+ id_x +"}]}"
    source_geojson = a1+a2+g1+i1
    """
    # Define WGS84 as CRS:
    geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')
    
    geo = []
    for idx, name_parcelle in enumerate(names):
        data_df = df.loc[(name_parcelle,),]
        
        lats = np.array(data_df.loc[:,"Lat"])
        lons = np.array(data_df.loc[:,"Lon"])
        
        # Compute:
        area, perim = geod.polygon_area_perimeter(lons, lats)
        
        dico = dict()
        coords = list(data_df.index)
        liste_coords = list()
        for coord in coords:
            Lat = df.loc[(name_parcelle,coord),"Lat"]
            Lon = df.loc[(name_parcelle,coord),"Lon"]
            liste_coords.append([Lat, Lon])
        liste_coords.append(liste_coords[0])
            
        geometry = {"coordinates": liste_coords, "type":"LineString"} # LineString, Polygon}
        
        feature = {"type":"Feature","properties":"{}","name": name_parcelle,
                   "geometry": geometry, "id": idx, "area": area, 
                   "perim": perim}
        
        #geo = dict()
        geo = {"type":"FeatureCollection", "features":[feature]}
        with open(f'{data_geo_save}/{name_parcelle}.geojson', 'w') as fp:
            json.dump(geo, fp)
        
    pass

def create_visu_geojson_OLD(data_path="projet_geo_assouinde",
                          data_geo_save="data_geojson", 
                          name_parcelle="P"):
    
    # Geojson data
    path = os.path.join( data_path, data_geo_save)
    number_files =  len(os.listdir(path))
    parcelles = []
    for i in range(1, number_files+1):
        parcelles.append(os.path.join(data_geo_save, f"{name_parcelle}{i}.geojson"))
        
    # Define WGS84 as CRS:
    geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')

    # Define folium object
    fl_n = folium.Map(location=[5.17564,-3.47634], tiles="OpenStreetMap", 
                      zoom_start=25)
    
    for i, parcelle in enumerate(parcelles):
        with open(parcelle) as f:
            gj = geojson.load(f)
        name = gj["features"][0]["name"]
        df_data = pd.DataFrame(gj["features"][0]["geometry"]["coordinates"], 
                               columns=["lat","lon"])
        
        # Compute:
        area, perim = geod.polygon_area_perimeter(df_data.lon, df_data.lat)
        area = round(abs(area), 3)
        perim = round(abs(perim), 3)
        
        gj["features"][0]["area"] = area
        
        html=f"""
            <h1> {name}</h1>
            <p>infos de la parcelle </p>
            <ul>
                <li>Surface: {area}</li>
                <li>Perimetre: {perim}</li>
                
            </ul>
            </p>
            <p>And that's a <a href="https://python-graph-gallery.com">link</a></p>
            """
        iframe = folium.IFrame(html=html, width=200, height=200)
        
        popup = folium.Popup(iframe, max_width=2650)
        
        folium.GeoJson( gj,
            popup=popup,
            highlight_function=lambda feature: {
                "fillColor": (
                    "green" if feature["area"] < 400 else "#ffff00"
                ),
            },
        ).add_to(fl_n)
        

    # Save the map again
    name_file = nom_site.split(".")[0]
    #fl_n.save("folium_geojson.html")
    fl_n.save(f"visu_folium_geojson_{name_file}.html")

    pass

###############################################################################
#                       new version  --- start
###############################################################################
def create_html(gj):
    html = ""
    name = gj["features"][0]["name"]
    area = gj["features"][0]["area"]
    perim = gj["features"][0]["perim"]
    a =f"""
        <h1> {name}</h1>
        <p>infos de la parcelle </p>
        <ul>
            <li>Surface: {area}</li>
            <li>Perimetre: {perim}</li>
        """
    Xs = ""
    coords = gj["features"][0]["geometry"]["coordinates"]
    for i, coord in enumerate(coords):
        X = f"<li> X{i} = ({coord[0], coord[1]}) </li> \n"
        Xs += X
        
    
    z = """
        </ul>
        </p>
        <p>And that's a <a href="https://python-graph-gallery.com">link</a></p>
        """
        
    html = a + Xs + z
    return html

def create_visu_geojson(data_path="projet_geo_assouinde",
                            data_geo_save="data_geojson", 
                            name_parcelle="P"):
    
    # Geojson data
    path = os.path.join( data_path, data_geo_save)
    number_files =  len(os.listdir(path))
    parcelles = []
    for i in range(1, number_files+1):
        parcelles.append(os.path.join(data_geo_save, f"{name_parcelle}{i}.geojson"))
        
    # Define WGS84 as CRS:
    geod = pyproj.Geod('+a=6378137 +f=0.003_352_810_664_747_512_6')

    # Define folium object
    fl_n = folium.Map(location=[5.17564,-3.47634], tiles="OpenStreetMap", 
                      zoom_start=25)
    
    for i, parcelle in enumerate(parcelles):
        with open(parcelle) as f:
            gj = geojson.load(f)
        name = gj["features"][0]["name"]
        df_data = pd.DataFrame(gj["features"][0]["geometry"]["coordinates"], 
                               columns=["lat","lon"])
        
        # Compute:
        area, perim = geod.polygon_area_perimeter(df_data.lon, df_data.lat)
        area = round(abs(area), 3)
        perim = round(abs(perim), 3)
        
        gj["features"][0]["area"] = area
        
        html = create_html(gj)
        
        iframe = folium.IFrame(html=html, width=200, height=200)
        
        popup = folium.Popup(iframe, max_width=2650)
        
        folium.GeoJson( gj,
            popup=popup,
            tooltip=folium.GeoJsonTooltip(fields=['code', 'name']),
            highlight_function=lambda feature: {
                "fillColor": (
                    "green" if feature["area"] < 400 else "#ffff00"
                ),
            },
        ).add_to(fl_n)
        

    # Save the map again
    name_file = nom_site.split(".")[0]
    #fl_n.save("folium_geojson.html")
    fl_n.save(f"visu_folium_geojson_{name_file}.html")

    pass
###############################################################################
#                       new version  --- End
###############################################################################


if __name__ == "__main__":
    
    nom_site = "assouande3parcelles.csv"
    nom_site = "assouande15parcelles.csv"
    nom_site = "assouande42parcelles.csv"
    data_path = "." # "geoVisu_Assouinde"
    #read_csv(data_path=data_path, nom_site=nom_site)
    
    creation_geojson_file(data_path=data_path, nom_site=nom_site)
    # create_visu_geojson_OLD(data_path=".",
    #                     data_geo_save="data_geojson", 
    #                     name_parcelle="P")
    create_visu_geojson(data_path=".",
                        data_geo_save="data_geojson", 
                        name_parcelle="P")
    pass
    