#include "utils.h"

std::vector<Job> swap(std::vector<Job> rt, int x, int y)
{
    /* Переворот куска тура: [x, y], включительно!
    :param route:
    :param x: индекс
    :param y: индекс
    :return: измененный список
    */
    std::vector <Job> route;
    for (auto i : rt) {
        route.push_back(Job(i));
    }

    int size = route.size();
    int temp = 0;
    if (x < y) {
        temp = (y - x + 1) / 2;
    } else if (x > y) {
        temp = ((size - x) + y + 2) / 2;
    }
    for (int i = 0; i < temp; i++) {
        int first = (x + i) % size;
        int second = (y - i) % size;
        Job j1(route[first]);
        route[first] = route[second];
        route[second] = j1;
    }
    std::vector <Job> route_vector;
    for (auto i : route) {
        route_vector.push_back(i);
    }
    return route_vector;
}

std::vector <Job> three_opt_exchange(std::vector <Job> rt, int best_exchange, std::tuple<int, int, int> nodes) {
    /* Изменение тура, после нахождения лучшего изменения 3-opt
    route:
    best_exchange: Тип замены
    nodes: Города
    return: Новый список городов
    */
    std::vector <Job> route;
    for (auto i : rt) {
        route.push_back(Job(i));
    }

    int x = std::get<0>(nodes);
    int y = std::get<1>(nodes);
    int z = std::get<2>(nodes);

    int s = route.size();

    int b = (x + 1) % s;
    int c = y % s;
    int d = (y + 1) % s;
    int e = z % s;
    if (best_exchange == 0) {
        route = swap(route, b, e);
    } else if (best_exchange == 1) {
        route = swap(route, d, e);
    } else if (best_exchange == 2) {
        route = swap(route, b, c);
    } else if (best_exchange == 3) {
        route = swap(swap(route, b, e), b, b + (e - d));
    } else if (best_exchange == 4) {
        route = swap(swap(swap(route, b, e), b, b + (e - d)), e - (c - b), e);
    } else if (best_exchange == 5) {
        route = swap(swap(route, b, e), e - (c - b), e);
    } else if (best_exchange == 6) {
        route = swap(swap(route, d, e), b, c);
    }
    return route;
}

std::tuple <std::vector<Job>, std::vector<Job>>
cross(std::vector <Job> route1, std::vector <Job> route2, int it1, int it2, int it3, int it4) {
    /* Cross-оператор - обмен кусками туров
    :param route1: тур один
    :param route2: тур два
    :param it1: тур один - начало куска
    :param it2: тур один - конец куска
    :param it3: тур два - начала куска
    :param it4: тур два - конец куска
    :return: новые туры
    */

    int size1 = route1.size();
    int size2 = route2.size();

    int new_size1 = size1 - (it2 - it1) + (it4 - it3);
    int new_size2 = size2 - (it4 - it3) + (it2 - it1);

    std::vector <Job> new_route1(new_size1);
    std::vector <Job> new_route2(new_size2);
    for (int i = 0; i < it1; i++) {
        new_route1[i] = route1[i];
    }
    for (int i = 0; i < it4 - it3 + 1; i++) {
        new_route1[i + it1] = route2[i + it3];
    }
    for (int i = 1; i < size1 - it2; i++) {
        new_route1[i + it1 + (it4 - it3)] = route1[i + it2];
    }

    for (int i = 0; i < it3; i++) {
        new_route2[i] = route2[i];
    }
    for (int i = 0; i < it2 - it1 + 1; i++) {
        new_route2[i + it3] = route1[i + it1];
    }
    for (int i = 1; i < size2 - it4; i++) {
        new_route2[i + it3 + (it2 - it1)] = route2[i + it4];
    }

    return std::make_tuple(new_route1, new_route2);
}

std::tuple <std::vector<Job>, std::vector<Job>>
replace(std::vector <Job> route1, std::vector <Job> route2, int it1, int it2) {
    /* Перемещение точки из тура 2 в тур 1
    :param route1: тур 1
    :param route2: тур 2
    :param it1: куда вставить
    :param it2: откуда вытащить
    :return: новые туры
    */
    int size1 = route1.size();
    int size2 = route2.size();
    std::vector <Job> new_route1(size1 + 1);
    std::vector <Job> new_route2(size2 - 1);

    for (int i = 0; i < size1 + 1; i++) {
        if (i == it1) {
            new_route1[i] = Job(route2[it2]);
        } else if (i < it1) {
            new_route1[i] = Job(route1[i]);
        } else {
            new_route1[i] = Job(route1[i - 1]);
        }
    }

    for (int i = 0; i < size2 - 1; i++) {
        if (i < it2) {
            new_route2[i] = Job(route2[i]);
        } else {
            new_route2[i] = Job(route2[i + 1]);
        }
    }

    return std::make_tuple(new_route1, new_route2);
}
