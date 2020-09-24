from itertools import product
from typing import List

import numpy as np


def assemble_matrix(subs: List[List[np.array]], small_size, full_size):
    res = np.zeros((full_size, full_size), dtype=np.int32)

    for i, j in product(range(len(subs)), r=2):
        i_from = i * small_size
        i_to = min((i + 1) * small_size, full_size)

        j_from = j * small_size
        j_to = min((j + 1) * small_size, full_size)

        res[i_from:i_to, j_from:j_to] = subs[i][j]

    return res

