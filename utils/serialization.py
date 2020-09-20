import gzip
import pickle
from typing import Any


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
    open_func = get_open_func(compression)
    with open_func(filename, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(filename, compression=None) -> Any:
    """
    Загрзуить объект из pickle
    :param compression: Используемое сжатие
    :param filename: Путь к файлу, из которого будем загружать
    :return: объект
    """
    open_func = get_open_func(compression)
    with open_func(filename, 'rb') as f:
        return pickle.load(f, fix_imports=True)
