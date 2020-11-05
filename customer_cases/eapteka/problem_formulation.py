import math
from pathlib import Path
from typing import List, Tuple, Sequence

import pandas as pd
import regex

from models.rich_vrp import Agent, AgentCosts, AgentType, Depot, Job
from models.rich_vrp.geometries.providers import OSRMMatrixGeometry
from models.rich_vrp.place_mapping import PlaceMapping
from models.rich_vrp.problem import RichVRPProblem


def build_eapteka_problem(data_folder: Path) -> RichVRPProblem:
    """
    Собираем из данных по аптеке RichVRPProblem

    Parameters
    ----------
    data_folder : папка, в которой находятся данные по eapteka

    Returns
    -------
    Построенная проблема, готовая к решению
    """

    # грузим данные
    points, stocks, couriers = load_data(
        coords_file=data_folder / "update_3.xlsx",
        orders_file=data_folder / "Заказы_13.xlsx",
        stocks_file=data_folder / "Склады.xlsx",
        couriers_file=data_folder / "Курьеры.xlsx",
    )

    # предобрабатываем датафреймы
    stocks_df = preprocess_stocks(stocks)
    couriers_df = preprocess_couriers(couriers)
    points_df = preprocess_points(points)

    # TODO: Добавить фильтры кривых точек (прямо в решалку?)
    # TODO: Заполнить недостающие веса заказа
    # TODO: Соединить склады
    # TODO: Конвертировать в инты, чтобы без потерь

    # TODO: Проставить агентам их отсутствующие ограничения
    # TODO: Проставить агентам их
    # TODO: Добавить в датафрейм delay (как к точкам, так и на склады)
    # TODO: Обработать повторные точки!

    # получаем классы из датафреймов
    depots = build_depots(stocks=stocks)
    agents = build_agents(agents_df=couriers_df)
    jobs = build_jobs(points=points_df, depots=stocks_df)

    return RichVRPProblem(
        place_mapping=build_place_mapping(depots=depots, jobs=jobs),
        agents=agents,
        jobs=jobs,
        depots=depots,
        objectives={},
    )


def build_place_mapping(
    depots: Sequence[Depot],
    jobs: Sequence[Job],
) -> PlaceMapping:
    """
    Создаем объект маппинга, который позволяет получать расстояния между точками, индексируясь самими точками.
    При первом вызове будет построена и соз

    Parameters
    ----------
    depots : Список депо
    jobs : Список джобов

    Returns
    -------
    PlaceMapping со всеми точками для задачи
    """
    return PlaceMapping(places=list(depots) + list(jobs), geometry_class=OSRMMatrixGeometry)


def build_agents(
    agents_df: pd.DataFrame,
) -> List[Agent]:
    """
    Билдим объекты Agent из DataFrame

    Parameters
    ----------
    agents_df : Датафрейм с агентами
    depots : Список всех существующих депо

    Returns
    -------
    Список агентов
    """

    # depots_dict = {d.name: d for d in depots}  # словрь депо, чтобы получать депо для точки
    return [
        Agent(
            id=row['id'],
            amounts=[row['weight'], row['volume']],
            time_windows=[row['t_from'], row['t_to']],
            name=row['name'],
            priority=row['priority'],
            # compatible_depots=depots_dict[row['depot']],
            # start_place=depots_dict[row['depot']],
            # end_place=depots_dict[row['depot']],

            costs=AgentCosts(time=row['cost']),
            type=AgentType(
                id=row['profile'],
                name=row['profile'],
                profile=row['profile'],
                capacities=None,
                skills=[],
            ),
        )
        for row in agents_df.iterrows()
    ]


def build_depots(
    stocks: pd.DataFrame,
) -> List[Depot]:
    """
    Билдим объекты Depot из складов

    Parameters
    ----------
    stocks : датафрейм со складами

    Returns
    -------
    Лист Depot
    """
    return stocks.map(
        lambda row: Depot(
            id=row.id,
            name=row.name,
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=row['delay'],
        )
    ).tolist()


def build_jobs(
    points: pd.DataFrame,
    depots: List[Depot],
) -> List[Job]:
    """
    Билдим Job из объектов нашего датафрейма.
    У каждой джобы есть прикрепленное депо.

    Parameters
    ----------
    points : Датафрейм точек
    depots : Лист Depot

    Returns
    -------
    Лист джобов
    """

    depots_dict = {d.name: d for d in depots}  # словрь депо, чтобы получать депо для точки

    return points.map(
        lambda row: Job(
            id=row.id,
            name=row.name,
            lat=row.lat,
            lon=row.lon,
            time_windows=[(row.t_from, row.t_to)],
            delay=row.delay,
            amounts=[row.weight, row.volume],
            price=row.price,
            priority=row.priority,
            depots=[depots[row.depot]],
        )
    ).tolist()


def load_data(
    coords_file: str,
    orders_file: str,
    stocks_file: str,
    couriers_file: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Загружем данные eapteka, принимая на вход все файлы

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
    """
    Препроцессим точки

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

    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype("int")
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")
    df["lat"] = df["Широта"].astype("float")
    df["lon"] = df["Долгота"].astype("float")

    # Убираем из названия склада MSK и пустое пространство
    df["name"] = df["Наименование"].map(lambda s: s[4:].strip())
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
    df["t_from"] = times.map(lambda x: regex.search(time_regex, x).group(1)).astype("int")
    df["t_to"] = times.map(lambda x: regex.search(time_regex, x).group(2)).astype("int")

    df["cost"] = df["Стоимость 1 заказа"].astype("int")
    df["profile"] = df["Должность"].map(lambda x: {"Курьер": "transport", "Водитель": "driver"}[x])
    df["name"] = df["Сотрудник"]
    df["priority"] = df["Приоритет"].map(lambda x: math.isfinite(x))
    df["id"] = df.index

    return df[["id", "name", "profile", "cost", "priority", "t_from", "t_to"]]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
