"""Это трансформер, который приводит задачу к решаемой растовский солвером."""
from typing import Dict, Tuple

import numpy as np
from boltons.iterutils import redundant
from more_itertools import flatten

from algorithms.transformers.base import BaseTransformer
from models.rich_vrp import VRPSolution, Place
from models.rich_vrp.problem import RichVRPProblem


class VrpCliTransformer(BaseTransformer):
    """Преобразуем проблему так, чтобы в ней не было повторных точек. """
    def __init__(self):
        self.duplicates_dict: Dict[Place, Tuple[float, float]] = {}

    def transform(
        self,
        problem: RichVRPProblem,
    ) -> RichVRPProblem:
        """Превращаем задачу в решаемую. """
        return self._deduplicate_points(problem)

    def restore(
        self,
        solution: VRPSolution,
    ) -> VRPSolution:
        """Восстанавливаем решение оригинальной задачи. """
        for p in solution.problem.places():
            p.lat, p.lon = self.duplicates_dict[p]

        return solution

    def _deduplicate_points(
        self,
        problem: RichVRPProblem
    ) -> RichVRPProblem:
        """Дедуплицируются точки в проблеме

        Сначала находятся одинаковые точки, потом к ним прибавляется небольшое число,
        чтобы их можно было считать разными
        """
        points = redundant(problem.places(), key=lambda p: (p.lat, p.lon), groups=True)

        for p in flatten(points):
            old_lat, old_lon = p.lat, p.lon
            p.lat += np.random.uniform(0, 1e-6)
            p.lon += np.random.uniform(0, 1e-6)
            self.duplicates_dict[p] = old_lat, old_lon

        return problem
