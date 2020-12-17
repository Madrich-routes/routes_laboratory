import subprocess
import sys
from typing import List


def exec_and_print(cmd: List[str]):
    """Перенаправляем входной и выходной поток запускаемой команды."""
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=subprocess.STDOUT)


def exec_and_iter(cmd: List[str]):
    """Итератор по выводимым строкам."""
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    yield from iter(popen.stdout.readline, "")

    popen.stdout.close()
    return_code = popen.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def exec_and_log(cmd: List[str], prompt: str = '>>'):
    """Печатает вывод подпроцесса с промптом."""
    lines = []
    for line in exec_and_iter(cmd):
        print(f"{prompt}: {line}", end='')
        lines += line

    return lines
