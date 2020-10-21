#include "vrp_problem.h"


bool VrpProblem::validate_skills(const Job &job, const Courier &courier) {
    // Проверяем, что задача подходит курьеру
    for (const auto &skill : job.skills) {
        bool found = (std::find(courier.skills.begin(), courier.skills.end(), skill) != courier.skills.end());
        if (!found) {
            return false;
        }
    }
    return true;
}

bool VrpProblem::validate_skills(const Storage &storage, const Courier &courier) {
    // Проверяем, что склад подходит курьеру
    for (const auto &skill : storage.skills) {
        bool found = (std::find(courier.skills.begin(), courier.skills.end(), skill) != courier.skills.end());
        if (!found) {
            return false;
        }
    }
    return true;
}

bool VrpProblem::validate_job(int travel_time, const Job &job, const Route &route) {
    // Проверяем, что поездка на эту задачу возможна
    int start_time = route.start_time;
    for (const auto &window : job.time_windows) {
        auto[start_shift, end_shift] = window.window;
        if ((start_shift <= start_time + travel_time) && (start_time + travel_time <= end_shift)) {
            return true;
        }
    }
    return false;
}

bool VrpProblem::validate_storage(int travel_time, const Route &route) {
    // Проверяем, что поездка на склад возможна
    auto[start_shift, end_shift] = route.storage.work_time.window;
    int start_time = route.start_time;
    if (!((start_shift <= start_time + travel_time) && (start_time + travel_time <= end_shift))) {
        return false;
    }
    return true;
}

bool VrpProblem::validate_courier(const State &state, const Route &route) {
    // Проверяем, что курьер еще жив
    // 1. проверяем время работы
    auto[start_shift, end_shift] = route.courier.work_time.window;
    int start_time = route.start_time;
    if (!((start_shift <= start_time + state.travel_time) && (start_time + state.travel_time <= end_shift))) {
        return false;
    }
    // 2. проверяем максимальную дистанцию
    if (state.distance > route.courier.max_distance) {
        return false;
    }
    // 3. проверяем на перевес
    int size_v = state.value.value().size();
    for (int i = 0; i < size_v; i++) {
        if (state.value.value()[i] > route.courier.value[i]) {
            return false;
        }
    }
    return true;
}

float VrpProblem::cost(int travel_time, int distance, const Route &route) {
    // Получение стоимости
    return route.courier.cost.start +
           float(travel_time) * route.courier.cost.second +
           float(distance) * route.courier.cost.meter;
}

State VrpProblem::start(const Route &route) {
    // Стартуем, едем от куда-то на склад
    std::vector distance_matrix = route.matrix.distance;
    std::vector travel_time_matrix = route.matrix.travel_time;

    int start_id = route.courier.start_location.matrix_id.value();
    int storage_id = route.storage.location.matrix_id.value();

    int tt = travel_time_matrix[start_id][storage_id];
    int d = distance_matrix[start_id][storage_id];

    Cost cost = route.courier.cost;
    float c = VrpProblem::cost(tt, d, route) + cost.start;
    State st(tt, d, c);
    return st;
}

State VrpProblem::end(int curr_point, const Route &route) {
    // Заканчиваем, едем с последней задачи в конечную точку
    std::vector distance_matrix = route.matrix.distance;
    std::vector travel_time_matrix = route.matrix.travel_time;

    int end_id = route.courier.end_location.matrix_id.value();
    int tt = travel_time_matrix[curr_point][end_id];
    int d = distance_matrix[curr_point][end_id];

    State st(tt, d, VrpProblem::cost(tt, d, route));
    return st;
}

std::optional<State> VrpProblem::go_job(int curr_point, const State &state, const Job &job, const Route &route) {
    // Оценка стоимости поездки на следующую задачу
    int tt = route.matrix.travel_time[curr_point][job.location.matrix_id.value()] + job.delay;
    int d = route.matrix.distance[route.storage.location.matrix_id.value()][job.location.matrix_id.value()];
    if (!VrpProblem::validate_job(state.travel_time + tt, job, route)) {
        return std::nullopt;
    }
    State tmp(tt, d, VrpProblem::cost(tt, d, route), std::optional<std::vector<int>>(job.value));
    if (!VrpProblem::validate_courier(tmp + state, route)) {
        return std::nullopt;
    }
    return tmp;
}

std::optional<State> VrpProblem::go_storage(int curr_point, const State &state, const Route &route) {
    // Оценка стоимости поездки на склад
    int tt = route.matrix.travel_time[curr_point][route.storage.location.matrix_id.value()] + route.storage.load;
    int d = route.matrix.distance[curr_point][route.storage.location.matrix_id.value()];
    if (!VrpProblem::validate_storage(state.travel_time + tt, route)) {
        return std::nullopt;
    }
    State s(tt, d, VrpProblem::cost(tt, d, route));
    return s;
}

std::optional<State> VrpProblem::next_job(int curr_point, const State &state, const Job &job, const Route &route) {
    // Получаем оценку стоимости поезкки на следующую задачу (со складом) """
    State new_state(state);
    std::optional<State> answer = VrpProblem::go_job(curr_point, new_state, job, route);
    if (!answer) {
        // 1. если не влезло едем на склад, если склад открыт и успеваем загрузиться до закрытия
        answer = VrpProblem::go_storage(curr_point, new_state, route);
        if (!answer) {
            return std::nullopt;
        }
        new_state += answer.value();
        std::vector<int> v(job.value.size());
        std::fill(v.begin(), v.end(), 0);  // check this
        new_state.value = v;
        // 2. едем на точку и успеваем отдать до конца окна
        answer = VrpProblem::go_job(route.storage.location.matrix_id.value(), new_state, job, route);
        if (!answer) {
            return std::nullopt;
        }
        new_state += answer.value();
    } else {
        new_state += answer.value();
    }
    return new_state;
}

Route VrpProblem::init_route(int vec,
                             Tour &tour,
                             const Courier &courier,
                             std::map<std::string, Matrix> &matrices) {
    // Строим жадно тур: по ближайшим подходящим соседям
    printf("Creating Route, Courier: %s, jobs: %llu, type: %s\n",
           courier.name.c_str(), tour.storage.unassigned_jobs.size(), courier.profile.c_str());

    Matrix matrix = matrices[courier.profile];
    Route route(vec, std::get<0>(courier.work_time.window), tour.storage, courier, matrix);

    int curr_point = route.storage.location.matrix_id.value();
    State state = VrpProblem::start(route);
    state.value = std::vector<int>(vec);

    while (tour.storage.unassigned_jobs.empty()) {
        std::optional<Job> best_job = std::nullopt;
        std::optional<State> best_state = std::nullopt;

        for (const auto &job : tour.storage.unassigned_jobs) {
            std::optional<State> answer = VrpProblem::next_job(curr_point, state, job, route);
            if (!answer) {
                continue;
            }

            State end = VrpProblem::end(job.location.matrix_id.value(), route);
            if (!VrpProblem::validate_courier(answer.value() + end, route)) {
                continue;
            }

            if ((!best_job) || (answer.value() < best_state.value())) {
                best_job = job;
                best_state = answer;
            }
        }
        if (!best_job) {
            break;
        }

        state = best_state.value();
        curr_point = best_job.value().location.matrix_id.value();
        route.jobs.push_back(best_job.value());
    }

    state += VrpProblem::end(curr_point, route);
    route.state = state;
    printf("Created Route, Jobs: %d\n", route.length());
    return route;
}


Tour VrpProblem::init_tour(int vec,
                           Storage &storage,
                           std::vector<Courier> &couriers,
                           std::map<std::string, Matrix> &matrices) {
    // Строим жадно тур: по ближайшим подходящим соседям для каждого курьера
    printf("Creating Tour: %s, Couriers: %llu, Jobs: %llu\n",
           storage.name.c_str(), couriers.size(), storage.unassigned_jobs.size());

    Tour tour(storage);
    for (const auto &courier : couriers) {
        if (!VrpProblem::validate_skills(storage, courier)) {
            continue;
        }
        Route route = VrpProblem::init_route(vec, tour, courier, matrices);
        tour.routes.push_back(route);
    }
    printf("Created Tour, Routes: %llu\n", tour.routes.size());
    return tour;
}


std::optional<State> VrpProblem::get_state(const Route &route) {
    int size_t = route.jobs.size();
    if (size_t == 0) {
        State st(0, 0, 0.0);
        return st;
    }

    int curr_point = route.storage.location.matrix_id.value();
    State state = VrpProblem::start(route);
    state.value = std::vector<int>(route.vec);

    for (const auto &job : route.jobs) {
        if (!VrpProblem::validate_skills(job, route.courier)) {
            return std::nullopt;
        }

        if (!VrpProblem::validate_courier(state, route)) {
            return std::nullopt;
        }

        std::optional<State> answer = VrpProblem::next_job(curr_point, state, job, route);
        if (!answer) {
            return std::nullopt;
        }
        if (!VrpProblem::validate_courier(answer.value(), route)) {
            return std::nullopt;
        }

        state = answer.value();
        curr_point = job.location.matrix_id.value();
    }

    state += VrpProblem::end(curr_point, route);
    if (!VrpProblem::validate_courier(state, route)) {
        return std::nullopt;
    }

    state.value = std::nullopt;
    return state;
}
