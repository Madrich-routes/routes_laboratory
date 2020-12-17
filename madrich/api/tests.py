import os
import time

import requests
import ujson

from madrich.api.app.solver import generate_random
from madrich.config import settings


def test_solver_point():
    data = open(generate_random("example.xlsx"), "rb")
    url = f"http://localhost:8000"
    files = {"file": data}
    r = requests.post(f"{url}/solver", files=files)
    job_id = r.json()["job_id"]
    print(r.json()["job_id"])

    flag, data = True, {}
    while flag:
        r = requests.get(f"{url}/status", params={"task_id": job_id})
        time.sleep(2)
        assert r.status_code == 200, f"fuck, reason: {r.reason}"
        data = r.json()
        flag = not data["is_finished"]
    assert data["result"], f"bad result from {url}/status"
    print(data["result"])


def test_random_task():
    url = f"http://localhost:8000"
    r = requests.post(f"{url}/random_task")
    job_id = r.json()["job_id"]
    print(r.json()["job_id"])

    flag, data = True, {}
    while flag:
        r = requests.get(f"{url}/status", params={"task_id": job_id})
        time.sleep(2)
        assert r.status_code == 200, f"fuck, reason: {r.reason}"
        data = r.json()
        flag = not data["is_finished"]
    assert data["result"], f"bad result from {url}/status"
    print(data["result"])


def test_example():
    url = f"http://localhost:8000"
    r = requests.get(f"{url}/example")
    if r.status_code == 200:
        path = settings.UPLOAD_DIR
        os.makedirs(path, exist_ok=True)
        with open(path / 'random_example.xlsx', "wb") as f:
            r.raw.decode_content = True
            f.write(r.content)
    else:
        print(r.status_code)
        print(r.json())
        print("big shit")


def test_get_excel():
    url = f"http://localhost:8000"
    with open('data/data.json', 'r') as f:
        data = ujson.load(f)
    r = requests.get(f'{url}/get_converted', json=data)
    if r.status_code == 200:
        path = settings.UPLOAD_DIR
        os.makedirs(path, exist_ok=True)
        with open(path / 'get_example.xlsx', "wb") as f:
            r.raw.decode_content = True
            f.write(r.content)
    else:
        print(r.status_code)
        print(r.json())
        print("big shit")
