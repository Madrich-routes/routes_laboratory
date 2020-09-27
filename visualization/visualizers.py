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

# TODO: graphviz visualizer
