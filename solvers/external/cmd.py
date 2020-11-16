import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


# subprocess.run(...).returncode == 0


# def exec_and_print(cmd: List[str]):
#     """
#     Перенаправляем входной и выходной поток запускаемой команды
#     """
#     subprocess.check_call(cmd, stdout=sys.stdout, stderr=subprocess.STDOUT)


class CommandRunner:
    """Класс для запуска произвольных команд.

    TODO: доделать (stderr, код завершения, время выполнения, статы, etc.), base_dir
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

        remove_output_files: bool = False,
        remove_input_files: bool = False,
    ):
        # сохраняем основные патаметры
        self.command = command
        self.files_dir = files_dir
        self.base_dir = base_dir
        self.input_files = {str(Path(self.files_dir) / f): d for f, d in input_files.items()}
        self.output_files = [str(Path(self.files_dir) / f) for f in output_files]

        # сохраняем опции
        self.remove_output_files = remove_output_files
        self.remove_input_files = remove_input_files
        self.show_stdout = show_stdout
        self.show_stderr = show_stderr

        self.stdout_prompt = stdout_prompt
        self.stderr_prompt = stderr_prompt

        # То, что получается на выходе
        self.output_files_data: Dict[str, str] = {}
        self.stdout: List[str] = []
        self.stderr: List[str] = []

    def run(self) -> 'CommandRunner':
        """Запустить команду на выполнение.

        Резульаты выполнения сохраняются в output_files_data, stdout, stderr
        """

        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.base_dir, exist_ok=True)

        # Считываем результаты, которые в файлах
        for filename, data in self.input_files.items():
            with open(filename, 'w') as f:
                f.write(str(data))

        self.stdout = self._exec_and_log()

        # Считываем результаты, которые в файлах
        for filename in self.output_files:
            with open(filename, 'r') as f:
                self.output_files_data[filename] = f.read()

        self._remove_files()

        return self

    def _remove_files(self) -> None:
        """Удаляем все ненужные файлы после решения."""
        files_to_remove = self.output_files * self.remove_output_files + self.input_files * self.remove_input_files

        for f in files_to_remove:
            try:
                os.remove(f)
            except Exception:  # noqa
                pass

    def _exec_and_iter(self):
        """Итератор по выводимым строкам."""
        popen = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        yield from iter(popen.stdout.readline, "")

        popen.stdout.close()
        return_code = popen.wait()

        if return_code:
            raise subprocess.CalledProcessError(return_code, self.command)

    def _exec_and_log(self):
        """Печатает вывод подпроцесса с промптом."""
        lines = []
        for line in self._exec_and_iter():
            print(f"{self.stdout_prompt}{line}", end='')
            lines += line

        return lines
