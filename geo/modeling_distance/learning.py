"""
Изучаем, как расстояние по прямой связано с расстоянием по дорогам в москве
"""
import geopy
import lightgbm as lgb
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import haversine_distances

from geo.providers import osrm
from geo.transforms import line_distance_matrix, haversine_numba
from utils.serialization import load_np, save_np, save_pickle, read_pickle

# matplotlib.use('QT4Agg', force=True)


def random_coords(size):
    coords = np.random.random(size=(size, 2))
    center = np.array([55.7558, 37.6173])

    lat_start = 55.572208
    lat_diff = 55.920812 - lat_start
    lon_start = 37.349728
    lon_diff = 37.860592 - lon_start

    coords[:, 1] *= lat_diff
    coords[:, 1] += lat_start

    coords[:, 0] *= lon_diff
    coords[:, 0] += lon_start

    return coords, center


def get_data(size):
    """
    Получаем набор данных для эксперимента
    """
    coords, center = random_coords(size)

    matrix = osrm.get_osrm_matrix(coords)

    save_np('points.npz', coords)
    save_np('osrm_matr.npz', matrix)


def build_features():
    """
    Билдим фичи, на которых учимся
    """
    points = load_np('points.npz')
    matrix = load_np('osrm_matr.npz')

    print(matrix)

    y = matrix.flatten()
    X = line_distance_matrix(points).flatten()

    print(X.shape)

    sns.scatterplot(X, y)
    plt.show()

    return X.reshape(-1, 1), y


def train_model():
    X, y = build_features()
    model = lgb.LGBMRegressor()
    model.fit(X, y)

    save_pickle('model.pkl', model)


def plot_test():
    model = read_pickle('model.pkl')

    test = np.linspace(0, 50000, num=1000)
    pred = model.predict(test.reshape(-1, 1))

    plt.plot(test, pred)
    plt.show()


if __name__ == "__main__":
    get_data(100)
    # train_model()
    # plot_test()
