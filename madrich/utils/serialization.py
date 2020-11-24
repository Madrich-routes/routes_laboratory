import gzip
import pickle
import sys
from sys import getsizeof
from typing import Any

import numpy as np
import ujson

from madrich.utils.logs import logger


def get_open_func(compression_alg="gzip"):
    """Возвращает функцию, с помощью которой фал открывается для чтения.

    :param compression_alg: алгоритм сжатия
    """
    if compression_alg is None:
        return open
    elif compression_alg == "gzip":
        return lambda *args, **kw: gzip.open(*args, **kw, compresslevel=5)


def save_pickle(filename, obj: object, compression=None):
    """Сохранить объект в pickle."""
    logger.debug(f"Сохраняем {filename} ({sys.getsizeof(obj)}) ...")
    open_func = get_open_func(compression_alg=compression)
    with open_func(filename, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(filename, compression=None) -> Any:
    """Загрзуить объект из pickle.

    :param compression: Используемое сжатие
    :param filename: Путь к файлу, из которого будем загружать
    :return: объект
    """
    logger.debug(f"Считываем {filename} ...")
    open_func = get_open_func(compression_alg=compression)
    with open_func(filename, "rb") as f:
        obj = pickle.load(f)

    logger.debug(f"Считали {filename} ({sys.getsizeof(obj)}) ...")
    return obj


# Методы для работы с numpy встроенным сохранением


def save_np(filename: str, a):
    logger.debug(f"Сохраняем матрицу {filename} ...")
    np.savez_compressed(filename, a)
    logger.debug(f"Сохранение закончено")


def load_np(filename: str):
    logger.debug(f"Загружаем матрицу {filename} ...")
    res = np.load(filename)["arr_0"]
    logger.debug(f"{filename} загрузили. {getsizeof(res)} байт")
    return res


# Методы для работы с json


def load_json(filename: str):
    logger.debug(f"Загружаем json {filename} ...")
    with open(filename) as f:
        obj = ujson.load(f)
    logger.debug(f"{filename} загрузили. {getsizeof(obj)} байт")
    return obj


def dump_json(filename: str, obj: Any):
    logger.debug(f"Сохраняем json {filename}. {getsizeof(obj)} байт")
    with open(filename, "wb") as f:
        ujson.dump(obj, f)
    logger.debug(f"{filename} загрузили. {getsizeof(obj)} байт")
    return obj


def save(filename: str, obj: Any):
    if isinstance(obj, np.ndarray):
        save_np(filename, obj)
    else:
        save_pickle(filename, obj)


def load(filename: str) -> Any:
    return pickle.load(filename)


def set_default(obj):
    if isinstance(obj, set) or isinstance(obj, frozenset):
        return list(obj)
    raise TypeError
