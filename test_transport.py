from geo.transport.matrix import build_dataset_from_files, build_walk_matrix
from geo.transport.calc_distance import build_graph
import pandas as pd
import numpy as np


def main():
    dataset = build_dataset_from_files()
    dataset.to_pickle('../data/full_df_refactored.pkl')
    walk_matrix = build_walk_matrix(dataset)
    dataset.to_pickle('../data/full_df_refactored.pkl')
    np.savez_compressed('../data/walk_matrix_refactored.npz', walk_matrix=walk_matrix)
    final_matrix_file = '../data/full_matrix_refactored.npz'
    final_mat = build_graph(dataset, walk_matrix, final_matrix_file)

if __name__ == "__main__":
    main()
