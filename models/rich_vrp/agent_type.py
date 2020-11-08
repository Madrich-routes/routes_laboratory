from typing import List


class AgentType:
    """Класс для описания общих характеристик агента. К одному типу относится то, что одинаково двигается,
    одинаково ограниченно, и умеет одинаковые штуки.

    Parameters
    ----------
    id : Уникальный идентификатор типа
    capacities : Вектор ограничения вместимости
    skills : Список имеющихся у типа скилов
    profile : Используемая типом геометрия (характеристики перемещения)
    name : Печатное имя
    """

    def __init__(
        self,
        id: int,
        capacities: List[int],
        skills: List[int],
        profile: str,
        name: str = '',
    ):
        self.id = id
        self.name = name

        self.profile = profile
        self.capacity_constraints: List[int] = capacities

        self.skills = skills

    def __str__(self):
        return f'Type(max_vol={self.capacity_constraints}, skills={self.skills}, profile={self.profile})'

    def __repr__(self) -> str:
        return str(self)

    def description(self):
        return f"{self.name} ({self.id})"
