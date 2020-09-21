import gzip
import pickle
from sys import getsizeof
from typing import Any

import numpy as np

from utils.logs import logger


def get_open_func(compression_alg="gzip"):
    """
    Возвращает функцию, с помощью которой фал открывается для чтения
    :param compression_alg: алгоритм сжатия
    """
    if compression_alg is None:
        return open
    elif compression_alg == 'gzip':
        return gzip.open


def save_pickle(filename, obj: object, compression=None):
    """
    Сохранить объект в pickle
    """
    open_func = get_open_func(compression_alg=compression)
    with open_func(filename, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(filename, compression=None) -> Any:
    """
    Загрзуить объект из pickle
    :param compression: Используемое сжатие
    :param filename: Путь к файлу, из которого будем загружать
    :return: объект
    """
    open_func = get_open_func(compression_alg=compression)
    with open_func(filename, 'rb') as f:
        return pickle.load(f)


def save_np(finename: str, a):
    logger.debug(f'Сохраняем матрицу {finename} ...')
    np.savez_compressed(finename, a)
    logger.debug(f'Сохранение закончено')


def load_np(finename: str):
    logger.debug(f'Загружаем матрицу {finename} ...')
    res = np.load(finename, allow_pickle=True)['arr_0']
    logger.debug(f'{finename} загрузили. {getsizeof(res)} байт')
    return res


def save(filename: str, obj: Any):
    if isinstance(obj, np.ndarray):
        save_np(filename, obj)
    else:
        save_pickle(filename, obj)


def load(filename: str) -> Any:
        return pickle.load(filename)
