"""
Утилиты, связанные с файловой системой
"""
import contextlib
import os


@contextlib.contextmanager
def chdir(dirname=None):
    """
    Контекстный менеджер, который позволяет изменить текущую дирректорию на входе и вернуть на выходе
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)
