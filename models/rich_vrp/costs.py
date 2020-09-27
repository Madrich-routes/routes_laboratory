from dataclasses import dataclass


@dataclass
class AgentCost:
    """
    Этот класс описывает изменения целевой функции для разных случаев
    """

    idle: int = 0  # стоимость простоя
    departure: int = 0,  # стоимость выхода в рейс
    load: int = 0,  # стоимость погрузки килограма
    time: int = 0,  # стоимость 1 секунды работы
    dist: int = 0,  # стоимость 1 метра проезда


