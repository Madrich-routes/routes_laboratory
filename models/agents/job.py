from dataclasses import dataclass


@dataclass
class Task:
    id: int  # индекс в матрице
    tw_start: str  # временные окна
    tw_end: str  # временные окна
    delay: float  # время обслуживания на точке
