"""
В этом модуле парсится json, содержащий данные о перемещениях метро.
"""
import json

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._shortest_path import floyd_warshall


def load_data(filename):
    with open(filename) as f:
        return json.load(f)


def build_graph(data):
    res = max(int(k) for k in data.keys())
    matrix = [[0] * (res + 1) for i in range(res + 1)]

    for sid1, station_data in data.items():
        for link in station_data['links']:
            # print(link)
            for sid2, dist in link.items():
                matrix[int(sid1)][int(sid2)] = dist

    graph = csr_matrix(matrix)

    dist_matrix, predecessors = floyd_warshall(csgraph=graph, directed=False, return_predecessors=True)

    return dist_matrix


def main():
    data = load_data('../../data/stations.json')
    matrix = build_graph(data)

    print(matrix[:10, :10])
    np.savez_compressed('metro_matrix.npz', matrix)


if __name__ == "__main__":
    main()
