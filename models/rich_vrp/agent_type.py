from typing import List

from models.rich_vrp.costs import AgentCost


class AgentType:
    """
    Класс для описания общих характеристик агента
    """

    def __init__(
            self,
            speed: int,  # скорость перемещения
            distance_matrix_id: int,  # его собственная матрица расстояний
            capacities: List[int],  # вектор ограничений
            costs: AgentCost,
            skills: List[int],  # список флагов, что он умеет
    ):
        # Характеристики перемещения
        self.speed: int = speed
        self.distance_matrix_id: int = distance_matrix_id

        self.capacity_constraints: List[int] = capacities
        self.costs = costs

        self.skills = skills

    def __str__(self):
        return f'Type(speed={self.speed * 3.6:.2f}, max_vol={self.capacity_constraints:.2f})'

    def __repr__(self) -> str:
        return str(self)
