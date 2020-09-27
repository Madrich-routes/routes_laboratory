# Drawing Moscow metro map using Folium

import folium
import os
import pandas as pd

red_square_coordinates = [55.7539, 37.6208]
metro_data = pd.read_csv('data/mos_metro.csv')
mos_map = folium.Map(location=red_square_coordinates, zoom_start=11)

line_data = {}

# 1) reading coordinates from CSV, 
# 2) Building data for drawing line / route
# 3) Drawing  markers/pins (metro stations)  in map

for index, row in metro_data.iterrows():
    lat = row['lat']
    lon = row['long']
    color = '#' + row['color']
    line_name = row['line']
    metro_name = row['name']

    # Add marker
    folium.Marker([lat, lon], tooltip = metro_name).add_to(mos_map)

    # Build data for Polyline
    # line_data = { 
    #           "Калининская": { 
    #                             "color"  : "#FFCD1C", 
    #                             "points" : [ [55.741125,37.626142],
    #                                          [55.7491,37.5395]]
    #                           }
    #         }
    if line_name in line_data:
        line_data[line_name]['points'] += [[lat, lon]]
    else:
        line_data[line_name] = { 'color': color, 'points': [[lat,lon]] }

# Drawing Metro route using line_data
for line_name in line_data:
    data = line_data[line_name]
    folium.PolyLine(data['points'], tooltip=line_name, color=data['color'], weight=5).add_to(mos_map)

#Write to Disk
mos_map.save('out/mos_map.html')
