import logging
import sys
from rich.console import Console

# Создаем logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Создаем форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создаем консольный обработчик логов
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

# Добавляем хендлер к логгеру. Их может быть много.
# Можно, например добавить хендлер с подробным логом в файл. TODO: сохранять все логи
logger.addHandler(handler)


# Консоль rich. Для красивой печати.
console = Console()
