"""Это трансформер, который приводит задачу к решаемой растовский солвером."""
from boltons.iterutils import redundant
from more_itertools import flatten

from algorithms.transformers.base import BaseTransformer
from models.rich_vrp import VRPSolution
from models.rich_vrp.problem import RichVRPProblem
import numpy as np

from solvers.madrich.examples.main_mdvrp import problem


class VrpCliTransformer(BaseTransformer):
    def __init__(self):
        self.duplicates_dict = {}


    def transform(self, problem: RichVRPProblem) -> RichVRPProblem:
        pass

    def restore(self, solution: VRPSolution) -> VRPSolution:
        pass

    def _deduplicate_points(
        self,
        problem: RichVRPProblem
    ) -> RichVRPProblem:
        """Дедуплицируются точки в проблеме

        Сначала находятся одинаковые точки, потом к ним прибавляется небольшое число,
        чтобы их можно было считать разными

        Returns
        -------
        """
        points = redundant(problem.places(), key=lambda p: (p.lat, p.lon), groups=True)

        for p in flatten(points):
            old_lat, old_lon = p.lat, p.lon
            p.lat += np.random.uniform(0, 1e-6)
            p.lon += np.random.uniform(0, 1e-6)
            self.duplicates_dict[p.id] = old_lat, old_lon

    def _restore_coords(self):
        for p in problem.places():
            ...
