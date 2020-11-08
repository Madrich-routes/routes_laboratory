import pandas as pd

from models.rich_vrp import VRPSolution


def save_info_excel(
        name: str,
        directory: str,
        solution: VRPSolution,
):
    file_name = (
        f"{name}_info.xlsx" if not directory else f"{directory}/{name}_info.xlsx"
    )
    writer = pd.ExcelWriter(file_name)