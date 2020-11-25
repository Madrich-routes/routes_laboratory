import time

import requests

from madrich.api.app.solver import generate_random

data = open(generate_random('example.xlsx'), 'rb')
url = f'http://localhost:8000'
files = {'file': data}
r = requests.post(f'{url}/solver', files=files)
job_id = r.json()['job_id']
print(r.json()['job_id'])

flag, data = True, {}
while flag:
    r = requests.get(f'{url}/status', params={'task_id': job_id})
    time.sleep(2)
    assert r.status_code == 200, f'fuck, reason: {r.reason}'
    data = r.json()
    flag = not data['is_finished']
assert data['result'], f'bad result from {url}/status'
print(data['result'])
