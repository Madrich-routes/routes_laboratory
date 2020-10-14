import pandas as pd
import matplotlib.pyplot as plt
import math
import math

import matplotlib.pyplot as plt
import pandas as pd


def main():
    data = pd.read_excel("data/update_3.xlsx")
    box = (36, 39.25, 55, 56.5)  # границы карты
    data = data[(data.lat > 55) & (data.lat < 56.5) & (data.lng > 36) & (
                data.lng < 39.25)]  # отбрасываем неверно геокодированные точки

    center = (sum(data.lat) / len(data.index), sum(data.lng) / len(data.index))  # нахождение центра масс точек
    max_dist = get_max_dist(data, center)  # посчитал максимум расстояний от центра, для ориентира при выборе радиуса

    radius = 0.5  # задаем ограничительный радиус для точек

    filtered_data = data[
        data.apply(lambda x: math.sqrt((x.lat - center[0]) ** 2 + (x.lng - center[1]) ** 2) < radius, axis=1)]
    print(len(data.index), len(filtered_data), len(filtered_data) / len(data))
    plot(filtered_data, box)
    # print(center, max_dist)


def get_max_dist(df, center):
    return max([math.sqrt((df.iloc[i].lat - center[0]) ** 2 + (df.iloc[i].lng - center[1]) ** 2) for i in
                range(len(df.index))])


def plot(df, box):
    map_back = plt.imread('data/map.png')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(df.lng, df.lat, zorder=1, c='b', s=10)
    ax.set_title('Ну, как-то так.')
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.imshow(map_back, zorder=0, extent=box, aspect='equal')
    plt.show()


if __name__ == "__main__":
    main()
