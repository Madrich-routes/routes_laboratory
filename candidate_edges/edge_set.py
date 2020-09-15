from collections import defaultdict
from typing import List

from models.graph.edge import Edge


class EdgeSet:
    def __init__(self, edges: List[Edge]):
        self.edges = set(edges)

        self.in_idx = defaultdict(list)
        self.out_idx = defaultdict(list)

        for e in edges:
            self.in_idx[e.end] += [e.start]
            self.out_idx[e.start] += [e.end]

    def __contains__(self, e: Edge):
        return e in self.edges
