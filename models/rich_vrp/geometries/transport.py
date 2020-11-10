import numpy as np
import pandas as pd
import os

import settings
from geo.transport.calc_distance import (
    build_graph,
    transport_travel_time,
)
from geo.transport.matrix import build_dataset_from_files, build_walk_matrix
from geo.providers import osrm_module

from models.rich_vrp.geometries.base import BaseGeometry
from utils.types import Array

transport_dataset_src = settings.DATA_DIR / "big/full_df_refactored_2210.pkl"
walk_matrix_src = settings.DATA_DIR / "big/walk_matrix_refactored_2210.npz"


class TransportMatrixGeometry(BaseGeometry):
    """
    Геометрия, позволяющая работать с общественным транспортом
    """
    def __init__(self, points: Array, distance_matrix: Array) -> None:
        super().__init__(points)

        self.d = distance_matrix  # расстояния пешком между точками

        # загрузим датасет остановок и матрицу расстояний пешком между ними
        if os.path.exists(transport_dataset_src):
            transport_dataset = pd.read_pickle(transport_dataset_src)
        else:
            transport_dataset = build_dataset_from_files()
            transport_dataset.to_pickle(transport_dataset_src)
        if os.path.exists(walk_matrix_src):
            walk_matrix = np.load(walk_matrix_src)["walk_matrix"]
        else:
            walk_matrix = build_walk_matrix(transport_dataset)
        np.savez_compressed(walk_matrix_src, walk_matrix=walk_matrix)

        transport_dist_matrix = build_graph(
            transport_dataset, walk_matrix
        )  # построим матрицу времен между остановками

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
        self.s_matrix = (transport_dist_matrix,)  # время проезда между точками
        self.closest_count: int = 10  # сколько ближайших остановок рассматривать

    def time(self, i: int, j: int, **kwargs) -> int:
        src_closest = self.p2s_matrix.argpartition(kth=self.closest_count, axis=1)[
            : self.closest_count
        ]
        dst_closest = self.s2p_matrix.T.argpartition(kth=self.closest_count, axis=1)[
            : self.closest_count
        ]
        result = transport_travel_time(
            i,
            j,
            self.p_matrix,
            self.p2s_matrix,
            self.s2p_matrix,
            self.s_matrix,
            src_closest,
            dst_closest,
        )
        return result[0]

    def dist(self, i: int, j: int, **kwargs) -> int:
        raise NotImplementedError
