"""В этом модуле расположены проверки корректности класса Job."""
from datetime import datetime, timedelta


def check_moscow_region(lat: float, lon: float) -> bool:
    """Очень грубая оценка по квадрату попаания точки в московскую область."""
    return (54.288066 < lat < 57.172201) and (34.619289 < lon < 39.724750)


def check_mcad(lat: float, lon: float) -> bool:
    """Проверяем по грубому квадрату попадание внутрь мкада."""
    return (55.572208 < lat < 55.920812) and (37.349728 < lon < 37.860592)


def check_year(dt: datetime, year: int = 2020) -> bool:
    """Проверяем принадлежность даты к году."""
    return dt.year == year


def check_delay(td: timedelta, max_days: int) -> bool:
    """Проверяем, что timedelta < days."""
    return 0 <= td.days < max_days


def check_time_window(tw_start: datetime, tw_end: datetime, max_window: int = 365):
    """Проверяем временное окно на адекватность max_window — максимальный допустимый размер временного окна в
    днях."""
    problems = [
        lambda: tw_start > tw_end,
        lambda: (tw_end - tw_start).days > max_window,
    ]

    return any(p() for p in problems)


def check_demand(demand: int):
    """Проверяем, что demand >= 0 и является интомм."""
    return isinstance(demand, int) and demand >= 0
