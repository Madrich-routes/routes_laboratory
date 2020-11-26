import numpy as np
import pandas as pd
import os

from madrich import config
from madrich.config import settings
from madrich.geo.transport.calc_distance import transport_travel_time, build_stations_matrix, build_graph
from madrich.geo.transport.matrix import build_dataset_from_files, build_walk_matrix
from madrich.geo.providers import osrm_module

from madrich.models.rich_vrp.geometries.base import BaseGeometry
from madrich.utils.types import Array

transport_dataset_src = settings.DATA_DIR / "big/full_df_refactored_2210.pkl"
walk_matrix_src = settings.DATA_DIR / "big/walk_matrix_refactored_2210.npz"
transport_matrix_src = settings.DATA_DIR / "big/full_matrix_refactored_2210.npz"


class TransportMatrixGeometry(BaseGeometry):
    """
    Геометрия, позволяющая работать с общественным транспортом
    """

    def __init__(self, points: Array, distance_matrix: Array) -> None:
        super().__init__(points)

        self.d = distance_matrix  # расстояния пешком между точками
        # загрузим датасет остановок
        if os.path.exists(transport_dataset_src):
            transport_dataset = pd.read_pickle(transport_dataset_src)
        else:
            transport_dataset = build_dataset_from_files()
            transport_dataset.to_pickle(transport_dataset_src)
        # загрузим матрицу расстояний между остановками
        if os.path.exists(transport_matrix_src):
            transport_dist_matrix = np.load(transport_matrix_src)
            transport_dist_matrix = transport_dist_matrix["matrix"]
        else:  # иначе, посчитаем заново
            if os.path.exists(walk_matrix_src):
                walk_matrix = np.load(walk_matrix_src)["walk_matrix"]
            else:
                walk_matrix = build_walk_matrix(transport_dataset)
                np.savez_compressed(walk_matrix_src, walk_matrix=walk_matrix)

            stations_matrix = build_stations_matrix(transport_dataset, walk_matrix)
            transport_dist_matrix = build_graph(stations_matrix)  # построим матрицу времен между остановками
        transport_stations_coords = list(transport_dataset["coord"])

        self.p_matrix = distance_matrix  # время пешком между точками
        _, self.p2s_matrix = osrm_module.get_osrm_matrix(
            src=points,
            dst=transport_stations_coords,
            transport="foot",
            return_distances=False,
        )  # время пешком от точек до остановок
        _, self.s2p_matrix = osrm_module.get_osrm_matrix(
            src=transport_stations_coords,
            dst=points,
            transport="foot",
            return_distances=False,
        )  # время пешком от остановок до точек
        self.s_matrix = transport_dist_matrix  # время проезда между точками
        self.closest_count: int = 10  # сколько ближайших остановок рассматривать

    def time(self, i: int, j: int, **kwargs) -> int:
        src_closest = self.p2s_matrix[i].argsort()[: self.closest_count]
        dst_closest = self.s2p_matrix.T[j].argsort()[: self.closest_count]
        result, _, _ = transport_travel_time(
            i,
            j,
            self.p_matrix,
            self.p2s_matrix,
            self.s2p_matrix,
            self.s_matrix,
            src_closest,
            dst_closest,
        )
        return result

    def dist(self, i: int, j: int, **kwargs) -> int:
        raise NotImplementedError

    def time_matrix(self) -> np.ndarray:
        res = np.empty(self.d.shape)
        for i in range(len(self.d)):
            for j in range(len(self.d)):
                res[i][j] = self.time(i, j)
        return res
