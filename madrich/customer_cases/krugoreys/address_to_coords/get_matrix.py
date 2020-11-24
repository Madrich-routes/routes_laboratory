import os

import numpy as np
import pandas as pd

from madrich.geo.providers.osrm_module import Point, get_osrm_matrix

df = pd.read_csv('./data/coordinates.csv', sep=';')
df.columns = ['address', 'lat', 'lon']

print(df.info())

points = tuple(Point(row.lat, row.lon) for row in df.itertuples())

os.environ["OSRM_HOST"] = "desktop"
os.environ["OSRM_PORT"] = '5000'

matrix = get_osrm_matrix(points)

# print(matrix)

np.savez_compressed('../big_data/small_matrix.npz', matrix)