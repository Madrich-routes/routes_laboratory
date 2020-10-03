from uuid import uuid4

import numpy as np

from models.rich_vrp.agent import Agent
from models.rich_vrp.geometry import BaseGeometry
from models.rich_vrp.job import Job
from typing import List


class RichVRPProblem:
    """
    Это класс RichVRP задачи — максимально общей постановки транспортной задачи.
    Его функция — описать все, что может встретиться в задаче в однозначной стандартной форме
    для использования во всем остальном коде и обеспечить легкий доступ к параметрам задачи.
    """
    def __init__(
            self,
            matrix: BaseGeometry,
            agents: List[Agent],
            jobs: List[Job],
            objectives: List[str],
    ):
        self.uuid = uuid4()  # уникальный id этой конкретной проблемы
        self.matrix = matrix
        self.agents = agents
        self.jobs = jobs
        self.objectives = objectives

