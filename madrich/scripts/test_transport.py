import numpy as np
import os
import pandas as pd

from madrich.geo import build_graph, build_stations_matrix
from madrich.geo.transport.matrix import build_dataset_from_files, build_walk_matrix


def main():
    dataset_filename = "../madrich/data/big/full_df_refactored_2210.pkl"
    if os.path.exists(dataset_filename):
        dataset = pd.read_pickle(dataset_filename)
    else:
        dataset = build_dataset_from_files()
        dataset.to_pickle(dataset_filename)

    # dataset = dataset[dataset['links']!={}]
    # dataset.to_pickle(dataset_filename+'2')

    walk_matrix_filename = "../madrich/data/big/walk_matrix_refactored_2210.npz"
    if os.path.exists(walk_matrix_filename):
        walk_matrix = np.load(walk_matrix_filename)["walk_matrix"]
    else:
        walk_matrix = build_walk_matrix(dataset)
        np.savez_compressed(walk_matrix_filename, walk_matrix=walk_matrix)

    final_matrix_file = "../madrich/data/big/full_matrix_refactored_2210.npz"
    if os.path.exists(final_matrix_file):
        final_mat = np.load(final_matrix_file)
    else:
        matrix = build_stations_matrix(dataset, walk_matrix)
        final_mat = build_graph(matrix)
        np.savez_compressed(final_matrix_file, walk_matrix=final_mat)


if __name__ == "__main__":
    main()
