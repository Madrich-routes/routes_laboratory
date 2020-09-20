from dataclasses import dataclass


@dataclass
class Jobs:
    id: int  # индекс в матрице
    tw_start: str  # временные окна
    tw_end: str  # временные окна
    delay: float  # время обслуживания на точке
    demand: int

    def tw_number(self):
        ...
