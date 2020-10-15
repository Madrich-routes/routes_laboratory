from pprint import pprint

import gmaps
import matplotlib.pyplot as plt
import numpy as np


def plot_yandex(points: np.ndarray):
    """
    Пример использования
    https://maps.yandex.ru/?rtext=54.483195,36.215616~52.722523,41.44807~54.630571,39.733868~54.007078,38.298298~54.483195,36.215616&rtt=auto&rtm=atm&apikey=7de5b730-c298-477f-a98f-fb355e9b3551
    """
    html = 'https://maps.yandex.ru/?rtext='
    html += '~'.join([f'{p[0]},{p[1]}' for p in points])
    html += '&rtt=auto&rtm=atm&apikey=7de5b730-c298-477f-a98f-fb355e9b3551'

    pprint(html)


def plot_tour(points, col="b"):
    """
    Рисуем один лепесток в matplotlib
    """
    plt.scatter(points[:, 0], points[:, 1], s=2, c="r")
    c = list(points) + [points[0]]
    plt.plot(*zip(*c), c=col, linewidth=0.5)


def plot_tours(routes, points, col=None):
    """
    Рисуем несколько лепестков в matplotlib
    """
    for r in routes:
        plot_tour(points[r], col=col)


def plot_on_gmaps(points: np.ndarray):
    """
    Рисуем маршрут на гугл-карте
    """
    fig = gmaps.figure()
    markers = gmaps.marker_layer(points)
    fig.add_layer(markers)

    return fig

# TODO: Tableau, PowerBI, FineReport, ArcGIS Online Platform

# TODO: mapboxgl, earthpy, rasterio
# TODO: spatialite
# TODO: pyecharts, plotly, folium, bokeh, basemap, geopandas

# Хорошие ссылки, которые можно посмотреть
# 1. https://pypi.org/project/gmaps/

# Можно рисовать норм карты через matplotlib
# https://jakevdp.github.io/PythonDataScienceHandbook/04.13-geographic-data-with-basemap.html

# https://www.coursera.org/projects/python-world-map-geovisualization-dashboard-covid-data

# Огненный курс
# https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-spatial-data/customize-raster-plots/interactive-maps/

# Тут есть про работу с геоjson и чем попало
# https://rosenfelder.ai/create-maps-with-python/

# https://developers.arcgis.com/python/guide/visualizing-data-with-the-spatial-dataframe/

# https://stackoverflow.com/questions/32649494/why-python-vincent-map-visuzalization-does-not-map-data-from-data-frame

# https://plotly.com/python/maps/

# https://medium.com/@minaienick/why-you-should-be-using-geopandas-to-visualize-data-on-maps-aka-geo-visualization-fd1e3b6211b4
# https://www.finereport.com/en/data-visualization/3-types-of-map-data-visualization-in-python.html
# https://towardsdatascience.com/level-up-your-visualizations-make-interactive-maps-with-python-and-bokeh-7a8c1da911fd
# https://towardsdatascience.com/a-complete-guide-to-an-interactive-geographical-map-using-python-f4c5197e23e0
# http://darribas.org/gds15/content/labs/lab_03.html
# https://programming.vip/docs/python-easy-map-visualization-with-detailed-source-code.html
# https://github.com/topics/map-visualization

# TODO: graphviz visualizer
