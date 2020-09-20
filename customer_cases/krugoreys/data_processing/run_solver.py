import gzip
import pickle

from solving.genetic_runner import run_genetic_solver

print('Матрица')
with gzip.open('../big_data/matrix.pkl.gz', 'rb') as f:
    d_matr = pickle.load(file=f)

with gzip.open('../big_data/vehicles.pkl.gz', 'rb') as f:
    vehicles = pickle.load(file=f)

with gzip.open('../big_data/tasks.pkl.gz', 'rb') as f:
    tasks = pickle.load(file=f)

for t in tasks:
    t.id -= 1

print('Начали решать')

run_genetic_solver(tasks, list(zip([1] * len(vehicles), vehicles)), d_matr)
