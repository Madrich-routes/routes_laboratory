import os
import pickle

import pandas as pd

from address_to_coords.osrm import Point, get_osrm_matrix

df = pd.read_csv('./coordinates.csv', sep=';')
df.columns = ['address', 'lat', 'lon']

print(df.info())

points = tuple(Point(row.lat, row.lon) for row in df.itertuples())

os.environ["OSRM_HOST"] = "desktop"
os.environ["OSRM_PORT"] = '5000'

matrix = get_osrm_matrix(points)

with open('res_matrix.pkl', 'wb') as f:
    pickle.dump(matrix, f)