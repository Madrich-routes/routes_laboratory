import os

import numpy as np
import pandas as pd

from geo.transport.calc_distance import build_graph
from geo.transport.matrix import build_dataset_from_files
from geo.transport.matrix import build_walk_matrix


def main():
    if os.path.exists('./data/full_df_refactored.pkl'):
        dataset = pd.read_pickle('./data/full_df_refactored.pkl')
    else:
        dataset = build_dataset_from_files()
        dataset.to_pickle('./data/full_df_refactored.pkl')
    walk_matrix = build_walk_matrix(dataset)
    np.savez_compressed('./data/walk_matrix_refactored.npz', walk_matrix=walk_matrix)
    final_matrix_file = './data/full_matrix_refactored.npz'
    final_mat = build_graph(dataset, walk_matrix, final_matrix_file)
    np.savez_compressed('./data/final_mat.npz', walk_matrix=final_mat)


if __name__ == "__main__":
    main()
