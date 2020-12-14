import pandas as pd
import numpy as np
import regex
import math
from copy import copy
from typing import Tuple, List, Dict

from pathlib import Path
from madrich.config import settings
from madrich.formats.excel.universal import StandardDataFormat
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.agent import Agent
from madrich.models.rich_vrp.depot import Depot
from madrich.solvers.vrp_cli.converters import str_to_ts


def import_eapteke(path: str, params: Dict[str, int]):
    """
    Собираем данные еаптеки в нашу эксельку

    Parameters
    ----------
    path : куда сохраняем

    Returns
    -------
    Наша экселька
    """

    # грузим данные
    points, stocks, couriers = load_data(
        coords_file=settings.DATA_DIR / "eapteka/data/update_3.xlsx",
        orders_file=settings.DATA_DIR / "eapteka/data/Заказы_13.xlsx",
        stocks_file=settings.DATA_DIR / "eapteka/data/Склады.xlsx",
        couriers_file=settings.DATA_DIR / "eapteka/data/Курьеры_13.xlsx",
    )

    # предобрабатываем датафреймы
    stocks_df = preprocess_stocks(stocks)
    couriers_df = preprocess_couriers(couriers)
    points_df = preprocess_points(points)

    fill_missing_columns(stocks=stocks_df, couriers=couriers_df, points=points_df, params=params)

    # получаем классы из датафреймов
    depots = build_depots(stocks=stocks_df)
    agents = build_agents(agents_df=couriers_df, depots=depots)
    jobs = build_jobs(points=points_df, depots=depots)

    StandardDataFormat.to_excel(agents, jobs, depots, path)


def load_data(
    coords_file: Path,
    orders_file: Path,
    stocks_file: Path,
    couriers_file: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Загружем данные eapteka, принимая на вход все файлы.

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
    coords = pd.read_excel(coords_file)
    orders = pd.read_excel(orders_file)
    stocks = pd.read_excel(stocks_file)
    couriers = pd.read_excel(couriers_file)

    points = coords.join(orders)

    return points, stocks, couriers


def preprocess_points(points: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Препроцессим точки.

    Parameters
    ----------
    points : pd.DataFrame
     Датафрейм с точками

    Returns
    -------
    Датафрейм, в котором колонки
    "id", "name", "depot", "geozone", "t_from", "t_to", "priority", "lat", "lon", "weight", "volume", "price"
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

    # фиксим окна с неправильным временем
    t_to[t_to <= t_from] = 24

    df["t_from"] = t_from.apply(get_timestamp)
    df["t_to"] = t_to.apply(get_timestamp)
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))  # парсим приоритет

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lng"].astype(float)

    df["geozone"] = df["ЗонаДоставки"]

    df["weight"] = df["ВесЗаказа"].fillna(0).map(lambda x: round(x * 1000)).astype(int)
    df["volume"] = df["ОбъемЗаказа"].fillna(0).map(lambda x: round(x * 1000000)).astype(int)
    df["price"] = df["СуммаДокумента"].fillna(0).astype(float)

    # Убираем из названия склада MSK и пустое пространство
    df["depot"] = df["Склад"].map(lambda s: s[4:].strip())

    df["name"] = df["corrected"]
    df["id"] = df.index

    # отсеиваем слишком удаленные точки
    center = (sum(df.lat) / len(df.index), sum(df.lon) / len(df.index))
    radius = 0.25
    df = df[df.apply(lambda x: math.sqrt((x.lat - center[0]) ** 2 + (x.lon - center[1]) ** 2) < radius, axis=1)]
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
    ].copy()


def preprocess_stocks(stocks: pd.DataFrame) -> pd.DataFrame:
    """Переименовываем колонки и фильтруем мусорные точки.

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

    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype("int")
    df["t_from"] = df["t_from"].apply(get_timestamp)
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")
    df["t_to"] = df["t_to"].apply(get_timestamp)
    df["lat"] = df["Широта"].astype("float")
    df["lon"] = df["Долгота"].astype("float")

    # Убираем из названия склада MSK и пустое пространство
    df["name"] = df["Наименование"].map(lambda s: s[4:].strip())
    df["type"] = "pharmacy"
    df.loc[df.name.str.contains("склад"), "type"] = "stock"

    df["id"] = df.index

    return df[["id", "name", "type", "lat", "lon", "t_from", "t_to"]].copy()


def preprocess_couriers(couriers: pd.DataFrame) -> pd.DataFrame:
    """Препрецессим данные курьеров.

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
    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype("int")
    df["t_from"] = df["t_from"].apply(get_timestamp)
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")
    df["t_to"] = df["t_to"].apply(get_timestamp)

    df["cost"] = df["Стоимость 1 заказа"].astype("int")
    df["profile"] = df["Должность"].map(lambda x: {"Курьер": "foot", "Водитель": "car"}[x])
    df["name"] = df["Сотрудник"]
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))
    df["id"] = df.index

    return df[["id", "name", "profile", "cost", "priority", "t_from", "t_to"]].copy()


def fill_missing_columns(
    stocks: pd.DataFrame, couriers: pd.DataFrame, points: pd.DataFrame, params: Dict[str, int]
) -> None:
    """Заполняем колонки, которых изначально в данных не было.

    Данные изменяются на месте

    Parameters
    ----------
    stocks : Склады
    couriers : Курьеры
    points : Заказы
    params : Недостающие данные
    """

    stocks.loc[:, "delay"] = params["delay_pharmacy"]
    stocks.loc[stocks.type == "stock", "delay"] = params["delay_stock"]

    couriers.loc[couriers.profile == "foot", "max_weight"] = params["pedestrian_max_weight"]
    couriers.loc[couriers.profile == "foot", "max_volume"] = params["pedestrian_max_volume"]

    couriers.loc[couriers.profile == "car", "max_weight"] = params["driver_max_weight"]
    couriers.loc[couriers.profile == "car", "max_volume"] = params["driver_max_volume"]

    points.loc[:, "delay"] = params["point_delay"]


def build_depots(
    stocks: pd.DataFrame,
) -> List[Depot]:
    """Билдим объекты Depot из складов.

    Parameters
    ----------
    stocks : датафрейм со складами

    Returns
    -------
    Лист Depot
    """
    return stocks.apply(
        lambda row: Depot(
            id=row.id,
            time_window=(row.t_from, row.t_to),
            name=row["name"],
            lat=row.lat,
            lon=row.lon,
            delay=row.delay,
        ),
        axis="columns",
    ).tolist()


def build_agents(
    agents_df: pd.DataFrame,
    depots: List[Depot],
) -> List[Agent]:
    """Билдим объекты Agent из DataFrame.

    Parameters
    ----------
    agents_df : Датафрейм с агентами
    depots : Список всех существующих депо

    Returns
    -------
    Список агентов
    """
    result = agents_df.apply(
        lambda row: Agent(
            id=int(row["id"]),
            name=row["name"],
            costs={"fixed": row["cost"], "distance": 0, "time": 0},
            capacity_constraints=[int(row["max_weight"]) * 1000, int(row["max_volume"]) * 100000],
            time_windows=[[row["t_from"], row["t_to"]]],
            compatible_depots=copy(depots),
            profile=row["profile"],
            skills=[],
        ),
        axis="columns",
    ).tolist()
    return result


def build_jobs(
    points: pd.DataFrame,
    depots: List[Depot],
) -> List[Job]:
    """Билдим Job из объектов нашего датафрейма. У каждой джобы есть прикрепленное депо.

    Parameters
    ----------
    points : Датафрейм точек
    depots : Лист Depot

    Returns
    -------
    Лист джобов
    """

    depots_dict = {d.name: d for d in depots}  # словрь депо, чтобы получать депо для точки

    return points.apply(
        lambda row: Job(
            id=row.id,
            name=row["name"] if str(row["name"]) != "nan" else "Неопределенный адрес",
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=row.delay,
            capacity_constraints=[row.weight, row.volume],
            price=row.price,
            priority=row.priority,
            depot=depots_dict[row.depot],
        ),
        axis="columns",
    ).tolist()


def get_timestamp(hours: int) -> int:
    """
    Получаем timestamp из кривого int часов.
    """
    if hours == 24:
        return str_to_ts(f"2020-10-01T23:59:59Z")
    else:
        return str_to_ts(f"2020-10-01T{hours}:00:00Z")


if __name__ == "__main__":
    params = {
        "delay_pharmacy": 5 * 60,
        "delay_stock": 10 * 60,
        "pedestrian_max_weight": 15,
        "pedestrian_max_volume": 40,
        "driver_max_weight": 15,
        "driver_max_volume": 40,
        "point_delay": 5,
    }
    import_eapteke(settings.DATA_DIR / "eapteka.xlsx", params)