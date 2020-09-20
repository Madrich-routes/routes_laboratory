from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Job:
    """
    Класс для описания работы, которую необходимо проделать агенту.
    Это самый общий класс. В него добавляются любые характеристики
    """
    id: int  # индекс в матрице
    tw_start: datetime  # временные окна
    tw_end: datetime  # временные окна
    delay: timedelta  # время обслуживания на точке
    demand: int

    # priority:

    # def tw_number(self):
    #     ...
