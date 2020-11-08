import random
from itertools import chain
from typing import List

# TODO: Мутации и скрещивания со множеством кандидатов

def invert(a: List[int]):
    """Тупой оператор, в котором мы просто переворачиваем кусок маршрута i включаем, j не включаем."""
    n = len(a)
    i, j = random.sample(range(n), 2)

    if i < j:
        a[i:j] = a[j - 1:i - 1:-1]
    else:
        size = n - i + j
        idx = chain(range(i, n), range(0, j))

        for i, v in enumerate(idx):
            if size - i <= i:
                break
            else:
                a[i], a[size - i] = a[size - i], a[i]
