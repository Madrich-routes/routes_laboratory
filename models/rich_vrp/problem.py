from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set
from uuid import uuid4

from models.rich_vrp import PlaceMapping, Agent, Job, Depot


class RichVRPProblem:
    """Это класс RichVRP задачи — максимально общей постановки транспортной задачи.

    Его функция — описать все, что может встретиться в задаче в однозначной стандартной форме для
    использования во всем остальном коде и обеспечить легкий доступ к параметрам задачи.

    Parameters
    ----------
    place_mapping : Объект, который умеет считать расстояние между точками
    agents : Список агентов, которые могут решать джобы в нашей задаче
    jobs : Список джоб, которые нужно выполнить в этой задаче
    depot : Список депо в этой задаче
    objectives : Критерии оптимизации для этой проблемы
    name : Название этой проблемы
    """

    def __init__(
        self,
        place_mapping: PlaceMapping,
        agents: List[Agent],
        jobs: List[Job],
        depot: Optional[Depot],
        objectives: List[str],
        name: Optional[str] = None
    ):
        self.name = name or uuid4()  # уникальный id этой конкретной проблемы
        self.matrix = place_mapping  # TODO: rename
        self.agents = agents
        self.jobs = jobs
        self.depot = depot
        self.objectives = objectives

    def info(self) -> str:
        """Базовая статистика проблемы.

        Returns
        -------
        Тескстовое представление статистики
        """
        return (
            f'problem_name: {self.name}, '
            f'agents: {len(self.agents)}, '
            f'jobs: {len(self.jobs)}, '
            f'objectives: {self.objectives}'
        )

    def profiles(self) -> Set[str]:
        """Получить список всех профайлов в проблеме.

        Returns
        -------
        Set всех профайлов
        """
        return {a.profile for a in self.agents}


class Profile(Enum):
    """Допустимые типы профайлов."""
    FOOT = 'foot'
    PEDESTRIAN = 'foot'

    BICYCLE = 'bicycle'
    BIKE = 'bicycle'

    CAR = 'car'
    VEHICLE = 'car'

    TRANSPORT = 'transport'
    TRANSPORT_SIMPLE = 'transport_simple'
