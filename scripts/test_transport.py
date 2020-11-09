import os

import numpy as np
import pandas as pd

from geo.transport.calc_distance import build_graph
from geo.transport.matrix import build_dataset_from_files, build_walk_matrix
from models.rich_vrp.geometries.transport import TransportMatrixGeometry
from geo.providers import osrm_module


def main():
    dataset_filename = "../data/big/full_df_refactored_2210.pkl"
    if os.path.exists(dataset_filename):
        dataset = pd.read_pickle(dataset_filename)
    else:
        dataset = build_dataset_from_files()
        dataset.to_pickle(dataset_filename)

    # dataset = dataset[dataset['links']!={}]
    # dataset.to_pickle(dataset_filename+'2')

    walk_matrix_filename = "../data/big/walk_matrix_refactored_2210.npz"
    if os.path.exists(walk_matrix_filename):
        walk_matrix = np.load(walk_matrix_filename)["walk_matrix"]
    else:
        walk_matrix = build_walk_matrix(dataset)
        np.savez_compressed(walk_matrix_filename, walk_matrix=walk_matrix)

    final_matrix_file = "../data/big/full_matrix_refactored_2210.npz"
    if os.path.exists(final_matrix_file):
        final_mat = np.load(final_matrix_file)
    else:
        final_mat = build_graph(dataset, walk_matrix)
        np.savez_compressed(final_matrix_file, walk_matrix=final_mat)


def transport_matrix_geometry_test():
    data = pd.read_excel("data/eapteka/data/update_3.xlsx")
    data = data.head(100)
    points = list((row.lat, row.lng) for row in data.itertuples())
    _, walk_matrix = osrm_module(src=points, transport="foot", return_distances=False)

    tmg = TransportMatrixGeometry(points, walk_matrix)
    t = tmg.time(10, 20)
    print(t)


if __name__ == "__main__":
    # main()
    transport_matrix_geometry_test()
