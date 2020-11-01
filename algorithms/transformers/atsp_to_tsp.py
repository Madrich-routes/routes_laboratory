import itertools

import numpy as np

INF = 1000000


class TSPExact:
    def __init__(self, matrix, redundant=False):
        """
        input: Adjacency matrix N x N
        len(nodes) = shape(input)
        @param matrix: N x N matrix
        @param redundant: false by default (n-1)!
        """
        # 1: Check if the adjacency matrix is symmetric
        self.cost_matrix = np.array(matrix)
        self.symmetry = None
        if self.symmetric() is False:
            self.symmetry = False
            self.as_symmetric()

        self.size = len(self.cost_matrix)
        self.nodes = range(self.size)
        self.all_tours = itertools.permutations

        if redundant is False:
            self.tours = self.non_redundant()
        else:
            self.tours = list(self.all_tours(self.nodes))

    def as_symmetric(self):
        """
        Переформулируем несимметричную TSP как симметриченую:
        "Jonker and Volgenant 1983"
        This is possible by doubling the number of nodes. For each city a dummy
        node is added: (a, b, c) => (a, a', b, b', c, c')

        distance = "value"
        distance (for each pair of dummy nodes and pair of nodes is INF)
        distance (for each pair node and its dummy node is -INF)
        ------------------------------------------------------------------------
          |A'   |B'   |C'   |A    |B    |C    |
        A'|0    |INF  |INF  |-INF |dBA  |dCA  |
        B'|INF  |0    |INF  |dAB  |-INF |dCB  |
        C'|INF  |INF  |0    |dAC  |dBC  |-INF |
        A |-INF |dAB  |dAC  |0    |INF  |INF  |
        B |dBA  |-INF |dBC  |INF  |0    |INF  |
        C |dCA  |dCB  |-INF |INF  |INF  |0    |

        [INF][A.T]
        [A  ][INF]
        """

        shape = len(self.cost_matrix)
        mat = np.identity(shape) * -INF + self.cost_matrix

        new_shape = shape * 2
        new_matrix = np.ones((new_shape, new_shape)) * INF
        np.fill_diagonal(new_matrix, 0)

        # insert new matrices
        new_matrix[shape:new_shape, :shape] = mat
        new_matrix[:shape, shape:new_shape] = mat.T
        # new cost matrix after transformation
        self.cost_matrix = new_matrix

    def total_tour(self, tour):
        total = sum(self.cost_matrix[tour[node], tour[(node + 1) % self.size]] for node in self.nodes)
        return total, tour

    def shortest(self):
        min_tour = min(self.total_tour(tour) for tour in self.tours)
        if self.symmetry is False:
            min_tour_real = min_tour[0] + self.size / 2 * INF
            min_cycle_real = min_tour[1][0::2]
            return min_tour_real, min_cycle_real
        else:
            return min_tour

    def non_redundant(self):
        start_node = self.nodes[0]
        new_set = list(self.nodes)[1:]
        return [list(np.append(start_node, tour)) for tour in self.all_tours(new_set)]

    def symmetric(self):
        """
        :return: True, если матрица симметричная
        """
        return (self.cost_matrix == self.cost_matrix.T).all()

    @property
    def tour_iterations(self):
        return list(self.tours)

    @property
    def tour_size(self):
        return self.size

    def mtsp_to_tsp(self, m: int) -> None:
        shape = len(self.cost_matrix)
        new_shape = shape + m - 1

        new_matrix = np.zeros((new_shape, new_shape))
        new_matrix[m:new_shape, m:new_shape] = self.cost_matrix

        for i in range(0, m-1):
            new_matrix[:, i] = new_matrix[:, m]
            new_matrix[i, :] = new_matrix[m, :]

        new_matrix[:m, :m] = INF  # mb zero is better
        self.cost_matrix = new_matrix
