from typing import List

from models.graph.distance_matrix import Geometry
from models.graph.edge import Edge
from models.graph.vertex import Vertex


class Graph:
    """
    Класс абстрактного графа.
    Возможно в проблеме лучше использвать его
    """
    def __init__(
            self,
            matrix: Geometry,
            vertices: List[Vertex],
            edges: List[Edge],
    ):
        """
        TODO: ребра и вершины можно расположить в хешмапах от индекса матрицы, чтобы получать доступ
        TODO: хранить вершины в ребрах, чтобы не было рассинхрона?
         Рассинхрон будет обязательно и будет бесить.
        """
        self.matrix = matrix
        self.vertices = vertices
        self.edges = edges

        assert len(self.matrix) == len(self.vertices)

    def size(self):
        return len(self.matrix)
