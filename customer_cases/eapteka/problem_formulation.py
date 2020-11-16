"""В этом модуле создаетяс проблема для eapteka."""
import math
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Sequence, Dict, Callable

import numpy as np
import pandas as pd
import regex
from fastcore.basics import with_cast

from models.rich_vrp import Agent, AgentCosts, AgentType, Depot, Job
from models.rich_vrp.geometries.base import BaseGeometry
from models.rich_vrp.place_mapping import PlaceMapping
from models.rich_vrp.problem import RichVRPProblem
from utils.types import Array


@dataclass
class AptekaParams:
    """Набор параметров, которые мы угадываем сами, так как в данных их нету."""
    delay_pharmacy: int
    delay_stock: int

    pedestrian_max_weight: int
    pedestrian_max_volume: int

    driver_max_weight: int
    driver_max_volume: int

    point_delay: int


def build_eapteka_problem(
    data_folder: Path,
    params: AptekaParams,
    profile_geometries: Dict[str, Callable[[Array], BaseGeometry]],
) -> RichVRPProblem:
    """Собираем из данных по аптеке RichVRPProblem.

    Parameters
    ----------
    data_folder : папка, в которой находятся данные по eapteka
    params : параметры, которые не указаны в основном датасете
    profile_geometries : Словарь profile -> функция. Функция должна принимать на вход точки и возвращать геометрию

    Returns
    -------
    Построенная проблема, готовая к решению
    """

    # грузим данные
    points, stocks, couriers = load_data(
        coords_file=data_folder / "update_3.xlsx",
        orders_file=data_folder / "Заказы_13.xlsx",
        stocks_file=data_folder / "Склады.xlsx",
        couriers_file=data_folder / "Курьеры_13.xlsx",
    )

    # предобрабатываем датафреймы
    stocks_df = preprocess_stocks(stocks)
    couriers_df = preprocess_couriers(couriers)
    points_df = preprocess_points(points)

    # TODO: Добавить фильтры кривых точек (прямо в решалку?)
    # TODO: Заполнить недостающие веса заказа
    # TODO: Соединить склады
    # TODO: Конвертировать в инты, чтобы без потерь

    # TODO: Проставить агентам их депо!
    # TODO: Обработать повторные точки!

    fill_missing_columns(stocks=stocks_df, couriers=couriers_df, points=points_df, params=params)

    # получаем классы из датафреймов
    depots = build_depots(stocks=stocks_df)
    agents = build_agents(agents_df=couriers_df, depots=depots)
    jobs = build_jobs(points=points_df, depots=depots)

    return RichVRPProblem(
        place_mapping=build_place_mapping(
            depots=depots,
            jobs=jobs,
            profile_geometries=profile_geometries
        ),
        agents=agents,
        jobs=jobs,
        depots=depots,
        objectives={},
    )


def fill_missing_columns(
    stocks: pd.DataFrame,
    couriers: pd.DataFrame,
    points: pd.DataFrame,
    params: AptekaParams,
) -> None:
    """Заполняем колонки, которых изначально в данных не было.

    Данные изменяются на месте

    Parameters
    ----------
    stocks : Склады
    couriers : Курьеры
    points : Заказы
    params : То, что мы подставляем
    """

    stocks.loc[:, 'delay'] = params.delay_pharmacy
    stocks.loc[stocks.type == 'stock', 'delay'] = params.delay_stock

    couriers.loc[couriers.profile == 'pedestrian', 'max_weight'] = params.pedestrian_max_weight
    couriers.loc[couriers.profile == 'pedestrian', 'max_volume'] = params.pedestrian_max_volume

    couriers.loc[couriers.profile == 'driver', 'max_weight'] = params.driver_max_weight
    couriers.loc[couriers.profile == 'driver', 'max_volume'] = params.driver_max_volume

    points.loc[:, 'delay'] = params.point_delay


def build_place_mapping(
    depots: Sequence[Depot],
    jobs: Sequence[Job],
    profile_geometries: Dict[str, Callable[[Array], BaseGeometry]],
) -> PlaceMapping:
    """Создаем объект маппинга, который позволяет получать расстояния между точками, индексируясь самими
    точками. При первом вызове будет построена и соз.

    Parameters
    ----------
    depots : Список депо
    jobs : Список джобов
    profile_geometries : Словарь profile -> функция. Функция должна принимать на вход точки и возвращать геометрию

    Returns
    -------
    PlaceMapping со всеми точками для задачи
    """
    places = list(depots) + list(jobs)
    points = np.array([[p.lat, p.lon] for p in places])

    geometries = {
        'driver': profile_geometries['driver'](points),
        'pedestrian': profile_geometries['pedestrian'](points),
    }

    return PlaceMapping(places=places, geometries=geometries)


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
    return agents_df.apply(
        lambda row: Agent(
            id=int(row['id']),
            amounts=[row['max_weight'], row['max_volume']],
            time_windows=[[row['t_from'], row['t_to']]],
            name=row['name'],
            priority=row['priority'],
            compatible_depots=copy(depots),

            start_place=None,  # эти поля будут заполняться потом
            end_place=None,

            costs=AgentCosts(time=row['cost']),
            type=AgentType(
                id=row['profile'],
                name=row['profile'],
                profile=row['profile'],
                capacities=[row['max_weight'], row['max_volume']],
                skills=[],
            ),
        ),
        axis='columns',
    ).tolist()

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
            name=row['name'],
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=row.delay,
        ),
        axis='columns',
    ).tolist()


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
            name=row['name'],
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=row.delay,
            amounts=[row.weight, row.volume],
            price=row.price,
            priority=row.priority,
            depots=[depots_dict[row.depot]],
        ),
        axis='columns'
    ).tolist()


@with_cast
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

    # фиксим окна с неправиьным временем
    t_to[t_to <= t_from] = 24

    df["t_from"] = t_from
    df["t_to"] = t_to
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))  # парсим приоритет

    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lng"].astype(float)

    df["geozone"] = df["ЗонаДоставки"]

    df["weight"] = df["ВесЗаказа"].fillna(0).astype(float)
    df["volume"] = df["ОбъемЗаказа"].fillna(0).astype(float)
    df["price"] = df["СуммаДокумента"].fillna(0).astype(float)

    # Убираем из названия склада MSK и пустое пространство
    df["depot"] = df["Склад"].map(lambda s: s[4:].strip())

    df["name"] = df["corrected"]
    df["id"] = df.index

    return df[
        ["id", "name", "depot", "geozone", "t_from", "t_to", "priority", "lat", "lon", "weight", "volume", "price"]
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
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")
    df["lat"] = df["Широта"].astype("float")
    df["lon"] = df["Долгота"].astype("float")

    # Убираем из названия склада MSK и пустое пространство
    df["name"] = df["Наименование"].map(lambda s: s[4:].strip())
    df["type"] = "pharmacy"
    df.loc[df.name.str.contains('склад'), "type"] = "stock"

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
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")

    df["cost"] = df["Стоимость 1 заказа"].astype("int")
    df["profile"] = df["Должность"].map(lambda x: {"Курьер": "pedestrian", "Водитель": "driver"}[x])
    df["name"] = df["Сотрудник"]
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))
    df["id"] = df.index

    return df[["id", "name", "profile", "cost", "priority", "t_from", "t_to"]].copy()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
