#include "route_utils.h"


std::vector<Job>
swap(const std::vector<Job> &jobs, int x, int y) {
    /* Переворот куска тура: [x, y], включительно!
    :param jobs:
    :param x: индекс
    :param y: индекс
    :return: измененный список
    */
    std::vector new_jobs = std::vector(jobs);
    int size = jobs.size();

    int temp = 0;
    if (x < y) {
        temp = (y - x + 1) / 2;
    } else if (x > y) {
        temp = ((size - x) + y + 2) / 2;
    }

    for (std::size_t i = 0; i < temp; ++i) {
        std::swap(new_jobs[(x + i) % size], new_jobs[(y - i) % size]);
    }

    return new_jobs;
}

std::vector<Job>
three_opt_exchange(const std::vector<Job> &jobs, int best_exchange, int x, int y, int z) {
    /* Изменение тура, после нахождения лучшего изменения 3-opt
    jobs:
    best_exchange: Тип замены
    nodes: Города
    return: Новый список городов
    */
    int size = jobs.size();

    int b = (x + 1) % size;
    int c = y % size;
    int d = (y + 1) % size;
    int e = z % size;

    if (best_exchange == 0) {
        return swap(swap(jobs, b, e), b, b + (e - d));
    } else if (best_exchange == 1) {
        return swap(swap(swap(jobs, b, e), b, b + (e - d)), e - (c - b), e);
    } else if (best_exchange == 2) {
        return swap(swap(jobs, b, e), e - (c - b), e);
    } else if (best_exchange == 3) {
        return swap(swap(jobs, d, e), b, c);
    } else if (best_exchange == 4) {
        return swap(jobs, b, e);
    } else if (best_exchange == 5) {
        return swap(jobs, d, e);
    } else if (best_exchange == 6) {
        return swap(jobs, b, c);
    } else {
        printf("Unexpected error!\n");
        return jobs;
        // throw std::invalid_argument("Bad exchange for three opt");
    }
}

std::tuple<std::vector<Job>, std::vector<Job>>
cross(const std::vector<Job> &jobs1, const std::vector<Job> &jobs2, int it1, int it2, int it3, int it4) {
    /* Cross-оператор - обмен кусками туров
    :param jobs1: тур один
    :param jobs2: тур два
    :param it1: тур один - начало куска
    :param it2: тур один - конец куска
    :param it3: тур два - начала куска
    :param it4: тур два - конец куска
    :return: новые туры
    */
    int size1 = jobs1.size();
    int size2 = jobs2.size();
    int new_size1 = size1 - (it2 - it1) + (it4 - it3);
    int new_size2 = size2 - (it4 - it3) + (it2 - it1);
    std::vector<Job> new_jobs1(new_size1);
    std::vector<Job> new_jobs2(new_size2);
    for (std::size_t i = 0; i < it1; ++i) {
        new_jobs1[i] = jobs1[i];
    }
    for (std::size_t i = 0; i < it4 - it3 + 1; ++i) {
        new_jobs1[i + it1] = jobs2[i + it3];
    }
    for (std::size_t i = 1; i < size1 - it2; ++i) {
        new_jobs1[i + it1 + (it4 - it3)] = jobs1[i + it2];
    }
    for (std::size_t i = 0; i < it3; i++) {
        new_jobs2[i] = jobs2[i];
    }
    for (std::size_t i = 0; i < it2 - it1 + 1; ++i) {
        new_jobs2[i + it3] = jobs1[i + it1];
    }
    for (std::size_t i = 1; i < size2 - it4; ++i) {
        new_jobs2[i + it3 + (it2 - it1)] = jobs2[i + it4];
    }
    return {new_jobs1, new_jobs2};
}

std::tuple<std::vector<Job>, std::vector<Job>>
replace_point(const std::vector<Job> &jobs1, const std::vector<Job> &jobs2, int it1, int it2) {
    /* Перемещение точки из тура 2 в тур 1
    :param jobs1: тур 1
    :param jobs2: тур 2
    :param it1: куда вставить
    :param it2: откуда вытащить
    :return: новые туры
    */
    int size1 = jobs1.size();
    int size2 = jobs2.size();
    std::vector<Job> new_jobs1(size1 + 1);
    std::vector<Job> new_jobs2(size2 - 1);

    for (std::size_t i = 0; i < size1 + 1; ++i) {
        if (i == it1) {
            new_jobs1[i] = jobs2[it2];
        } else if (i < it1) {
            new_jobs1[i] = jobs1[i];
        } else {
            new_jobs1[i] = jobs1[i - 1];
        }
    }

    for (std::size_t i = 0; i < size2 - 1; ++i) {
        if (i < it2) {
            new_jobs2[i] = jobs2[i];
        } else {
            new_jobs2[i] = jobs2[i + 1];
        }
    }

    return {new_jobs1, new_jobs2};
}
