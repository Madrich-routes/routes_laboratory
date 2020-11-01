import os

import numpy as np
import pandas as pd

from geo.providers.osrm_module import get_osrm_matrix
from geo.transport.calc_distance import build_graph
from geo.transport.matrix import build_dataset_from_files, build_walk_matrix


def main():
    dataset_filename = '../data/full_df_refactored_2210.pkl'
    if os.path.exists(dataset_filename):
        dataset = pd.read_pickle(dataset_filename)
    else:
        dataset = build_dataset_from_files()
        dataset.to_pickle(dataset_filename)


    # dataset = dataset[dataset['links']!={}]
    # dataset.to_pickle(dataset_filename+'2')

    walk_matrix_filename = '../data/walk_matrix_refactored_2210.npz'
    if os.path.exists(walk_matrix_filename):
        walk_matrix = np.load(walk_matrix_filename)['walk_matrix']
    else:
        walk_matrix = build_walk_matrix(dataset)
        np.savez_compressed(walk_matrix_filename, walk_matrix=walk_matrix)

    final_matrix_file = '../data/full_matrix_refactored_2210.npz'
    if os.path.exists(final_matrix_file):
        final_mat = np.load(final_matrix_file)['matrix']
    else:
        final_mat = build_graph(dataset, walk_matrix, final_matrix_file)
        # np.savez_compressed(final_matrix_file, walk_matrix=final_mat)

    return

# def build_final_matrix():
#     ...


if __name__ == "__main__":
    main()
