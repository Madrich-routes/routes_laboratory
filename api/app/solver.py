import os

from settings import UPLOAD_DIR


def run_solver(filename: str) -> dict:
    print(os.path.exists(f'{UPLOAD_DIR}/{filename}'))
    return {"gut": "done"}
