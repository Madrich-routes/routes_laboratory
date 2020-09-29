import matplotlib.pyplot as plt
import numpy as np


def main():
    nodes, service_time = open_file('./VRPTW/files/INSTANCES/Solomon_25/C101.25.3.vrptw')
    distance_matrix = get_distance_matrix(nodes)
    # res = clarc_wright(nodes, distance_matrix)
    # dist = calculate_route_distance(res, distance_matrix)
    # print(res, dist)
    # plot_result(nodes, res)

    # res = closest_neighbour(nodes, distance_matrix.copy())
    # dist = calculate_route_distance(res, distance_matrix)
    # print(res, dist)
    # plot_result(nodes, res)

    res = solomon(nodes, distance_matrix, service_time, 'min_time')
    dist = calculate_route_distance(res, distance_matrix)
    print(res, dist)
    plot_result(nodes, res)


# Метод Кларка-Райта, можно посмотреть, например, тут: https://infostart.ru/1c/articles/443585/
def clarke_wright(nodes, distance_matrix):
    count = len(nodes)
    s = np.zeros((count, count))  # построение матрицы выиграшей в расстоянии
    for i in range(1, count):
        for j in range(i + 1, count):
            distance_benefit = distance_matrix[0][i] + distance_matrix[0][j] - distance_matrix[i][j]
            s[i][j] = distance_benefit

    res, routed_places = [], []
    while (True):  # Повторяем, пока все элементы матрицы выиграшей не обработаны
        max = np.unravel_index(np.argmax(s, axis=None), s.shape)  # Получаем ребро с наибольшим выишрашем
        if max == (0, 0):  # Если текущее максимальное ребро (0,0) - выходим из цикла
            break
        if max[0] not in routed_places and max[
            1] not in routed_places:  # добавляем новый маршрут, если ни одна из точек ранее не была добавлена
            res.append([max[0], max[1]])
            routed_places.append(max[0])
            routed_places.append(max[1])
        elif max[0] not in routed_places or max[1] not in routed_places:
            for i in range(len(
                    res)):  # если новая точка содержится в текущих маршрутах присоединяем новую точку к данному маршруту
                if res[i][0] == max[0]:
                    res[i].insert(0, max[1])
                    routed_places.append(max[1])
                elif res[i][-1] == max[0]:
                    res[i].append(max[1])
                    routed_places.append(max[1])
                elif res[i][0] == max[1]:
                    res[i].insert(0, max[0])
                    routed_places.append(max[0])
                elif res[i][-1] == max[1]:
                    res[i].append(max[0])
                    routed_places.append(max[0])
        else:  # если обе точки задействованы в существующий маршрутах, проверяем нельзя ли их соединить
            for i in range(len(res)):
                for j in range(i + 1, len(res)):
                    if res[i][0] in max and res[j][0] in max:
                        res[i].reverse()
                        res[i] += res[j]
                        res.remove(res[j])
                    elif res[i][0] in max and res[j][-1] in max:
                        res[j] += res[i]
                        res.remove(res[i])
                    elif res[i][-1] in max and res[j][0] in max:
                        res[i] += res[j]
                        res.remove(res[j])
                    elif res[i][-1] in max and res[j][-1] in max:
                        res[i].reverse()
                        res[j] += res[i]
                        res.remove(res[i])
        s[max[0]][max[1]] = 0  # отмечаем использованные ребра в матрице выиграшей
    return res


# Метод ближайших соседей
def closest_neighbour(nodes, distance_matrix):
    res = [0]  # Инициализиуем начальное состояние результирующего списка
    for j in range(len(nodes)):  # Зануляем столбец в матрице расстояний до 0-ой вершины
        distance_matrix[j][res[-1]] = 0
    for i in range(len(nodes) - 1):
        min_val = min(i for i in distance_matrix[res[-1]] if
                      i > 0)  # На каждом шаге находим ближайшую вершину к последней добавленной в маршрут
        min_index = list(distance_matrix[res[-1]]).index(min_val)
        res.append(min_index)
        for j in range(len(nodes)):  ##Зануляем столбец в матрице расстояний до последней добавленной вершины
            distance_matrix[j][res[-1]] = 0
    return [res[1:]]


# Эвристика Соломона I1
def solomon(nodes, distance_matrix, service_time, seed_node):
    alpha1, alpha2, mu, lam = 0.5, 0.5, 2, 5  # Задаем коэффициенты
    res = []  # Список маршрутов
    route = []  # Текущий маршрут
    unrouted_nodes = [i for i in range(1, len(nodes))]  # Список непосещенных вершин
    while (len(unrouted_nodes) > 0):  # повторять, пока все вершины не посещены
        if (len(route) == 0):  # если терущий маршрут пустой, разаем его корневой вершиной
            seed_index = unrouted_nodes[0]
            if (
                    seed_node == 'max_len'):  # выбор корневой вершины по принципу поиска максимального расстояния от 0-ой вершины
                max_len = distance_matrix[0][unrouted_nodes[0]]
                for i in unrouted_nodes:
                    if distance_matrix[0][i] > max_len:
                        max_len = distance_matrix[0][i]
                        seed_index = i
            else:  # корневой вершиной выбирается та, у которой временное окно открывается раньше всех
                min_time = nodes[unrouted_nodes[0]][2]  # стартовое состояния поиска ближайшего времени доставки
                for i in unrouted_nodes:
                    if nodes[i][2] < min_time:
                        min_time = nodes[i][2]
                        seed_index = i
            route = [0, seed_index, 0]
            unrouted_nodes.remove(seed_index)  # Удаляем добавленную вершину в маршрут из списка непосещенных
        max_val = 0
        max_pos = (-1,
                   -1)  # Инициализация наилучшей позиции вставки, где max_pos[0] - врешина, max_pos[1] - позиция вставки в тек. маршрут
        for u in unrouted_nodes:  # Проходим по каждой вершине
            time = 0  # Время, от начала пути, до предыдущего пункта
            for j in range(len(route) - 1):  # Проходим по каждому месту вставки
                if (time + distance_matrix[route[j]][u] < nodes[u][
                    3] and  # Проверяем, проходим ли мы в тек. месте вставки во временные рамки тек. вершины
                        max(time + distance_matrix[route[j]][u], nodes[u][2]) + service_time + distance_matrix[u][
                            route[j + 1]] < nodes[route[j + 1]][3]):
                    c11 = distance_matrix[route[j]][u] + distance_matrix[route[j + 1]][u] - mu * \
                          distance_matrix[route[j]][route[j + 1]]  # Рассчет параметров(см. статью)
                    c12 = (time + distance_matrix[route[j]][u] + service_time + distance_matrix[u][route[j + 1]]) - (
                            time + distance_matrix[u][route[j + 1]])
                    c1 = alpha1 * c11 + alpha2 * c12
                    c2 = lam * distance_matrix[0][u] - c1
                    if c2 >= max_val:  # Поиск максимально выгодной вставки
                        max_val = c2
                        max_pos = (u, j)
                time += distance_matrix[route[j]][
                            route[j + 1]] + service_time  # Добавление времени до предыдущей вершины
        if (max_val > 0):  # Если нашли место оптимальной вставки - добавляем в текущий маршрут
            route.insert(max_pos[1] + 1, max_pos[0])
            unrouted_nodes.remove(max_pos[0])
        else:  # Противном случае - завершаем текущий маршрут и сознаем новый
            res.append(route)
            route = []
    if (len(route) > 0):
        res.append(route)
    return res


# Рассчет матрицы расстояний
def get_distance_matrix(nodes):
    count = len(nodes)
    distance_matrix = np.zeros((count, count))
    for i in range(count):
        for j in range(i, count):
            delX = nodes[i][0] - nodes[j][0]
            delY = nodes[i][1] - nodes[j][1]
            distance = (delX * delX + delY * delY) ** (1 / 2)
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance
    return distance_matrix


# Чтение данных из файла
def open_file(path):
    with open(path) as f:
        text = f.readlines()
    coords_start = 9
    service_time = int(text[5].split(":")[1])
    count = int(text[2].split(":")[1])
    coords = text[coords_start:coords_start + count]
    time_windows = text[coords_start + 2 * count + 2:coords_start + 3 * count + 2]

    # Структура nodes = [x, y, начало временного окна, конец временного окна]

    nodes = [[int(coords[i].split()[1]), int(coords[i].split()[2]),
              int(time_windows[i].split()[1]), int(time_windows[i].split()[2])] for i in range(len(coords))]
    return nodes, service_time


# ------------ СЕРВИСНЫЕ ФУНКЦИИ -----------------
def check_fesibility(res, nodes, distance_matrix, service_time):
    res = []
    for route in res:
        time = 0
        for i in range(1, len(route) - 1):
            time += max(distance_matrix[route[i - 1]][route[i]] + service_time, nodes[route[i]][2])
            if (time >= nodes[route[i][3]]):
                res.append(False)
                break
    return res


def calculate_route_distance(routes, distance_matrix):
    res = []
    for route in routes:
        cur_len = 0
        for i in range(len(route) - 1):
            cur_len += distance_matrix[i][i + 1]
        cur_len += distance_matrix[0][route[0]]
        cur_len += distance_matrix[0][route[-1]]
        res.append(cur_len)
    return res


def plot_result(nodes, routes):
    x, y = [], []
    for i in range(len(nodes)):
        x.append(nodes[i][0])
        y.append(nodes[i][1])
        plt.text(nodes[i][0] + 0.1, nodes[i][1] + 0.1, i)
    plt.plot(x, y, 'ro')
    for route in routes:
        x = [nodes[i][0] for i in route]
        y = [nodes[i][1] for i in route]
        x.insert(0, nodes[0][0])
        y.insert(0, nodes[0][1])
        x.append(nodes[0][0])
        y.append(nodes[0][1])
        plt.plot(x, y, c=np.random.rand(3, ))
    plt.show()


if __name__ == "__main__":
    main()
