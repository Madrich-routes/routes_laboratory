import pandas as pd

from madrich.models.rich_vrp.solution import VRPSolution


def save_info_excel(
        name: str,
        directory: str,
        solution: VRPSolution,
):
    file_name = (
        f"{name}_info.xlsx" if not directory else f"{directory}/{name}_info.xlsx"
    )
    writer = pd.ExcelWriter(file_name)
