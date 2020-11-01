import os
import subprocess
import sys
from typing import List, Dict


def exec_and_print(cmd: List[str]):
    """
    Перенаправляем входной и выходной поток запускаемой команды
    """
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=subprocess.STDOUT)


def exec_and_iter(cmd: List[str]):
    """
    Итератор по выводимым строкам
    """
    popen = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def exec_and_log(cmd: List[str], prompt: str = '>>'):
    """
    Печатает вывод подпроцесса с промптом
    """
    lines = []
    for line in exec_and_iter(cmd):
        print(f"{prompt}: {line}", end='')
        lines += line

    return lines


class CommandRunner:
    """
    Класс для запуска произвольных команд.
    TODO: доделать
    """

    def __init__(
            self,
            command: str,
            input_files: Dict[str, str],
            output_files: List[str],

            files_dir: str,
            base_dir: str,

            show_stdout: bool = True,
            show_stderr: bool = True,

            stdout_prompt: str = '>>',
            stderr_prompt: str = '!!',

            remove_files: bool = False,
    ):
        self.command = command
        self.input_files = input_files
        self.output_files = output_files

        self.remove_files = remove_files
        self.files_dir = files_dir
        self.base_dir = base_dir

        self.stdout

    def remove_files(self):
        for f in self.output_files:
            os.remove(self.output_files)

    def run(self):
