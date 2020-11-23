from dataclasses import dataclass

from models.rich_vrp import Place


@dataclass
class Visit:
    place: Place
    activity: str
    arrival: int  # секунды с начала мира, когда приехал на точку
    departure: int  # секунды с начала мира, когда уехал на точку
