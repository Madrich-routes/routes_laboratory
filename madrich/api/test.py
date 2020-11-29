import time
import os
import requests
from madrich.config import settings
from madrich.api.app.solver import generate_random

# solver test
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

# random_task test
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

# example test

r = requests.post(f"{url}/example")
if r.status_code == 200:
    path = settings.DATA_DIR / "tmp/tests"
    os.makedirs(path, exist_ok=True)
    with open(path, "wb") as f:
        r.raw.decode_content = True
        f.write(r.content)
