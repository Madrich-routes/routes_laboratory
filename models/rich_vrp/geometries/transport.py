
import numpy as np
import scipy, os

from geo.transport.calc_distance import build_graph, combined_matrix, transport_travel_time
from geo.transport.matrix import build_dataset_from_files, build_walk_matrix

from models.rich_vrp.geometries.base import BaseGeometry
from utils.types import Array

transport_dataset_src = '../data/big/full_df_refactored_2210.pkl'

class TransportMatrixGeometry(BaseGeometry):
    """
    Геометрия, позволяющая работать с общественным транспортом
    """
    def __init__(
        self,
        points: Array,
        distance_matrix: Array
    ) -> None:
        super().__init__(points)

        self.d = distance_matrix  # расстояния пешком между точками

        #загрузим матрицы
        if os.path.exists(transport_dataset_src):
                transport_dataset = pd.read_pickle(transport_dataset_src)
            else:
                transport_dataset = build_dataset_from_files()
                transport_dataset.to_pickle(transport_dataset_src)
                
        transport_dist_matrix = build_graph(transport_dataset, distance_matrix, '')# договориться и пофиксить
            

        #!!!Разобраться как перевести то, что написано выше, в то, что написано ниже

        self.p_matrix: Array = None,  # время пешком между точками
        self.p2s_matrix: Array = None,  # время пешком от точек до остановок
        self.s2p_matrix: Array = None,  # время пешком от остановок до точек
        self.s_matrix: Array = None,  # время проезда между точками

        self.closest_count: int = 10 # сколько ближайших остановок рассматривать

    def time(self, i: int, j: int, **kwargs) -> int
        src_closest = self.p2s_matrix.argpartition(kth=self.closest_count, axis=1)[:self.closest_count]
        dst_closest = self.s2p_matrix.T.argpartition(kth=self.closest_count, axis=1)[:self.closest_count]
        result = transport_travel_time(i, j, self.p_matrix, self.p2s_matrix, self.s2p_matrix, self.s_matrix, src_closest, src_closest)
        return result[0]