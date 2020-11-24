import random

from madrich.utils.types import Array

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence


# TODO: что такое strategy и strategy crossover?
# TODO: ordered должно быть норм


def one_point(ind1: Array, ind2: Array):
    """Одноточечный кросовер.

    Просто обмениваемся начальными кусками последовательности.
    """
    size = min(len(ind1), len(ind2))
    cp = random.randint(1, size - 1)
    ind1[cp:], ind2[cp:] = ind2[cp:], ind1[cp:]


def two_point(ind1: Array, ind2: Array):
    """Двуточечный кросовер.

    Меняем кусок из середины.
    """
    size = min(len(ind1), len(ind2))
    cp1, cp2 = crossover_points(size)
    ind1[cp1:cp2], ind2[cp1:cp2] = ind2[cp1:cp2], ind1[cp1:cp2]


def messy(ind1: Array, ind2: Array):
    """Обмениваемся началами разной длины."""
    cp1 = random.randint(0, len(ind1))
    cp2 = random.randint(0, len(ind2))
    ind1[cp1:], ind2[cp2:] = ind2[cp2:], ind1[cp1:]


def uniform(ind1: Array, ind2: Array, swap_proba: float):
    """Свапаем переменные с некоторой вероятностью.

    (Можно для кажджой штуки свою)
    """
    size = min(len(ind1), len(ind2))

    for i in range(size):
        if random.random() < swap_proba:
            ind1[i], ind2[i] = ind2[i], ind1[i]

    return ind1, ind2


def pmx(ind1: Array, ind2: Array):
    """Partially matched crossover.

    Parameters
    ----------
    ind1 :
    ind2 :

    Returns
    -------
    """
    size = min(len(ind1), len(ind2))
    p1, p2 = [0] * size, [0] * size

    # Initialize the position of each indices in the individuals
    for i in range(size):
        p1[ind1[i]] = i
        p2[ind2[i]] = i

    # Choose crossover points
    cp1, cp2 = crossover_points(size)

    # Apply crossover between cx points
    for i in range(cp1, cp2):
        # Keep track of the selected values
        temp1, temp2 = ind1[i], ind2[i]

        # Swap the matched value
        ind1[i], ind1[p1[temp2]] = temp2, temp1
        ind2[i], ind2[p2[temp1]] = temp1, temp2
        # Position bookkeeping
        p1[temp1], p1[temp2] = p1[temp2], p1[temp1]
        p2[temp1], p2[temp2] = p2[temp2], p2[temp1]

    return ind1, ind2


# def uniform_partially_matched():
#     """
#
#     """


# ---------------------------------------------- utilities function -----------------------------------------------

def crossover_points(size: int):
    return sorted(random.sample(range(size + 1), 2))
