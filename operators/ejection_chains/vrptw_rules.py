"""
По мотивам статей
https://core.ac.uk/download/pdf/6941901.pdf
https://wwwhome.ewi.utwente.nl/~uetzm/Preprints/ejection_chain_paper.pdf
"""
from typing import List

from candidate_edges.edge_set import EdgeSet
from models.problems.cvrptw import CVRPTWProblem


# TODO: Изучить https://www.cirrelt.ca/documentstravail/cirrelt-2017-75.pdf


class Solution:
    def __init__(
            self,
            problem: CVRPTWProblem,
            tours: List[List[int]],
            candidates: EdgeSet,
    ):
        self.problem = problem
        self.tours = tours
        self.candidates = candidates
        self.depot = 0

    def cross(self, c1: int, c2: int):
        """
        c1, c2 — удаляемое ребро.

        Находим одного из боижайших соседей c1, которые в другом туре.
        """
        ...
