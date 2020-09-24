"""
Модуль, чтобы смержить дурцкие Димины эксельки в нормальный вид
"""
from collections import defaultdict

import pandas as pd
from pandas import ExcelWriter


def get_dfs(filename: str):
    """
    Получаем все датафреймы. И их имена, сгруппированные по общей части.
    """
    xl = pd.ExcelFile(filename)
    names = xl.sheet_names

    dfs = defaultdict(list)
    name_dict = defaultdict(list)

    for name in names:
        common = name[:15]
        df = xl.parse(name)

        dfs[common] += [df]
        name_dict[common] += [name]

    return dfs, name_dict


def longest_common_prefix(strs):
    """
    Получаем общий префикс
    """
    longest_pre = ""

    if not strs:
        return longest_pre

    shortest_str = min(strs, key=len)

    for i in range(len(shortest_str)):
        if all([x.startswith(shortest_str[:i + 1]) for x in strs]):
            longest_pre = shortest_str[:i + 1]
        else:
            break

    return longest_pre


def marge_tables(dfs, names):
    """
    Объединяем таблицы и их имена
    """
    res_dict = {}
    for n in names.keys():
        the_name = longest_common_prefix(names[n])
        the_df = pd.concat(dfs[n])

        res_dict[the_name] = the_df

    return res_dict


def write_sheets(filename, data):
    """
    Записываем все на диск
    """
    with ExcelWriter(filename) as writer:
        for name, df in data.items():
            df.to_excel(writer, sheet_name=name)


def merge_couriers(in_file, out_file):
    """
    Мержим файл с курьерами-листами
    """
    dfs, names = get_dfs(in_file)
    merged = marge_tables(dfs, names)
    write_sheets(out_file, merged)


if __name__ == "__main__":
    merge_couriers('./data/solver_10_couriers.xlsx', './data/fixed_couriers.xlsx')
