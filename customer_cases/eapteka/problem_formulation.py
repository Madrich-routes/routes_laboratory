import math
from pathlib import Path
from typing import Tuple, List

import pandas as pd
import regex

from models.rich_vrp import Job, Depot, Agent, AgentType, AgentCosts


def build_eapteka_problem(data_folder: Path):
    points, stocks, couriers = load_data(
        coords_file=data_folder / "update_3.xlsx",
        orders_file=data_folder / "Заказы_13.xlsx",
        stocks_file=data_folder / "Склады.xlsx",
        couriers_file=data_folder / "Курьеры.xlsx",
    )

    stocks = preprocess_stocks(stocks)
    couriers = preprocess_couriers(couriers)
    points = preprocess_points(points)


def build_agents(
        stocks: pd.DataFrame,
):
    drivers_type = AgentType(
        id=0,
        speed=None,
        name='driver',
        capacities=None,
        costs=AgentCosts(),
        skill=[],
    )

    transport_type = AgentType(
        id=0,
        speed=None,
        name='driver',
        capacities=None,
        costs=AgentCosts(),
        skill=[],
    )

    stocks.map(
        lambda row: Agent(
            id=row.id,
            name=row.name,
            time_windows=[(row.t_from, row.t_to)],
            start_place=None,
            end_place=None,

        )
    )


def build_depots(
        stocks: pd.DataFrame,
):
    stocks.map(
        lambda row: Depot(
            id=row.id,
            name=row.name,
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=0,
        )
    )


def build_jobs(
        points: pd.DataFrame,
        stocks: pd.DataFrame,
) -> List[Job]:
    """
    Билдим Job из объектов нашего датафрейма

    Parameters
    ----------
    points : Датафрейм точек

    Returns
    -------
    Лист джобов
    """

    points.map(
        lambda row: Job(
            id=row.id,
            name=row.name,
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=0,
            amounts=[row.weight, row.volume, row.price],
            price=row.price,
            priority=row.priority,
        )
    )


def load_data(
        coords_file: str,
        orders_file: str,
        stocks_file: str,
        couriers_file: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Загружем данные eapteka

    Parameters
    ----------
    coords_file : файл с геокоднутыми координатами
    orders_file : файл с заказами
    stocks_file : файл со складами
    couriers_file : файл с курьерами

    Returns
    -------
    pd.DataFrame, датафреймы со складами и с точкамиы
    """
    coords = pd.read_excel(coords_file, engine="openpyxl")  # xlrd пока сломан в 3.9
    orders = pd.read_excel(orders_file, engine="openpyxl")
    stocks = pd.read_excel(stocks_file, engine="openpyxl")
    couriers = pd.read_excel(couriers_file, engine="openpyxl")

    points = coords.join(orders)

    return points, stocks, couriers


def preprocess_points(points: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Препроцессим точки

    Parameters
    ----------
    points : pd.DataFrame
     Датафрейм с точками

    Returns Tuple[pd.Series, pd.Series]
      t_from, t_to — ряды с часами
    -------
    """
    df = points

    # вытаскиваем время из строки
    time_regex = r"Доставка с ([0-9]{0,2}).* по ([0-9]{0,2}).*$"
    times = df["ИнтервалДоставки"]
    t_from = times.map(lambda x: regex.search(time_regex, x).group(1))
    t_to = times.map(lambda x: regex.search(time_regex, x).group(2))

    # фиксим отсутствующие
    t_to[t_to == ""] = "24"
    t_from[t_from == ""] = "00"

    # фиксим типы данных
    t_to = t_to.astype(int)
    t_from = t_from.astype(int)

    # фиксим окна с неправиьным временем
    t_to[t_to <= t_from] = 24

    df["t_from"] = t_from
    df["t_to"] = t_to
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lng"].astype(float)

    df["geozone"] = df["ЗонаДоставки"]

    df["weight"] = df["ВесЗаказа"].fillna(0).astype(float)
    df["volume"] = df["ОбъемЗаказа"].fillna(0).astype(float)
    df["price"] = df["СуммаДокумента"].fillna(0).astype(float)

    df["depot"] = df["Склад"]

    df["name"] = df["corrected"]
    df["id"] = df.index

    return df[
        [
            "id",
            "name",
            "depot",
            "geozone",
            "t_from",
            "t_to",
            "priority",
            "lat",
            "lon",
            "weight",
            "volume",
            "price",
        ]
    ]


def preprocess_stocks(
        stocks: pd.DataFrame,
) -> pd.DataFrame:
    """
    Переименовываем колонки и фильтруем мусорные точки

    Parameters
    ----------
    stocks : Склады

    Returns
    -------
    Склады которые распарсили
    """
    df = stocks

    time_regex = r"([0-9]{0,2})-([0-9]{0,2})$"
    times = df["График работы"].replace("круглосуточно", "0-24")

    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype(
        "int"
    )
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")
    df["lat"] = df["Широта"].astype("float")
    df["lon"] = df["Долгота"].astype("float")
    df["name"] = df["Наименование"]
    df["id"] = df.index

    return df[["id", "name", "lat", "lon", "t_from", "t_to"]]


def preprocess_couriers(couriers: pd.DataFrame) -> pd.DataFrame:
    """
    Препрецессим данные курьеров

    Parameters
    ----------
    couriers : датафрейм с информацией о курьерах

    Returns
    -------
    Датафрейм с дополнительный информацией
    """
    df = couriers
    time_regex = r"([0-9]{0,2})-([0-9]{0,2})$"
    times = df["Интервал работы"]
    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype(
        "int"
    )
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")

    df["cost"] = df["Стоимость 1 заказа"].astype("int")
    df["profile"] = df["Должность"].map(
        lambda x: {"Курьер": "transport", "Водитель": "driver"}[x]
    )
    df["name"] = df["Сотрудник"]
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))
    df["id"] = df.index

    return df[["id", "name", "profile", "cost", "priority", "t_from", "t_to"]]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
