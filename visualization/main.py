import folium

mos_map = folium.Map(location=[55.7539, 37.6208], zoom_start=11)

line_data = {}

routes = [[], []]

for r in routes:


for lat, lon in data:
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

mos_map.save('out/mos_map.html')
