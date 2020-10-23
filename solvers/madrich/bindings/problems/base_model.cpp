#include "base_model.h"

// TODO: Нормальный логгинг


//// Window


Window::Window(std::tuple<int, int> window) : window(std::move(window)) {}

int to_seconds(const std::string &time) {
    std::tm t{};
    std::istringstream ss(time);
    ss >> std::get_time(&t, "%Y-%m-%dT%H:%M:%SZ");
    return std::mktime(&t);
}

Window::Window(const std::string &start_t, const std::string &end_t) {
    window = std::tuple<int, int>(to_seconds(start_t), to_seconds(end_t));
}

[[maybe_unused]] void Window::print() const {
    printf("start: %d, end: %d\n", std::get<0>(window), std::get<1>(window));
}


//// Point


Point::Point(std::optional<int> matrix_id, std::tuple<float, float> point, std::optional<std::string> addr)
        : matrix_id(matrix_id), point(std::move(point)), address(std::move(addr)) {}

[[maybe_unused]] void Point::print() const {
    printf("Point: %f %f id: %d\n",
           std::get<0>(point), std::get<1>(point),
           matrix_id.has_value() ? matrix_id.value() : -1);
}


//// Cost


Cost::Cost(float start, float second, float meter) : start(start), second(second), meter(meter) {}

[[maybe_unused]] void Cost::print() const {
    printf("%f %f %f\n", second, meter, start);
}


//// Matrix


Matrix::Matrix(std::string profile, std::vector<std::vector<int>> distance, std::vector<std::vector<int>> travel_time)
        : profile(std::move(profile)), distance(std::move(distance)), travel_time(std::move(travel_time)) {}

[[maybe_unused]] void Matrix::print() const {
    printf("Matrix: %s, size: %llu\n", profile.c_str(), distance.size());
}


//// State


State::State(int travel_time, int distance, float cost, std::optional<std::vector<int>> value)
        : travel_time(travel_time), distance(distance), cost(cost), value(std::move(value)) {}

[[maybe_unused]] void State::print() const {
    printf("State; travel time: %d, distance: %d, cost: %f\n", travel_time, distance, cost);
}

std::optional<std::vector<int>> State::sum_values(const State &lt, const State &rt) {
    if ((!lt.value.has_value()) && (!rt.value.has_value())) {
        return std::nullopt;
    } else if (lt.value.has_value() && !rt.value.has_value()) {
        return lt.value;
    } else if (!lt.value.has_value() && rt.value.has_value()) {
        return rt.value;
    } else {
        int size = lt.value.value().size();
        std::optional ret = std::vector<int>(size);
        std::vector<int> ltv = lt.value.value();
        std::vector<int> rtv = rt.value.value();
        for (std::size_t i = 0; i < size; ++i) {
            ret.value()[i] = ltv[i] + rtv[i];
        }
        return ret;
    }
}

State State::operator+(const State &rhs) const {
    return State(travel_time + rhs.travel_time, distance + rhs.distance, cost + rhs.cost, sum_values(*this, rhs));
}

State &State::operator+=(const State &rhs) {
    travel_time += rhs.travel_time;
    distance += rhs.distance;
    cost += rhs.cost;
    value = sum_values(*this, rhs);
    return *this;
}

bool State::operator<(const State &rhs) const {
    if (travel_time != rhs.travel_time) {
        return travel_time < rhs.travel_time;
    }
    if (cost != rhs.cost) {
        return cost < rhs.cost;
    }
    if (distance != rhs.distance) {
        return distance < rhs.distance;
    }
    return false;
}


//// Job


Job::Job(int delay,
         std::string job_id,
         std::vector<int> value,
         std::vector<std::string> skills,
         const Point &location,
         std::vector<Window> time_windows)
        : job_id(std::move(job_id)), delay(delay), value(std::move(value)),
          skills(std::move(skills)), location(location), time_windows(std::move(time_windows)) {}

[[maybe_unused]] void Job::print() const {
    printf("Job id: %s\n", job_id.c_str());
}


bool Job::operator==(const Job &other) const {
    return other.job_id == job_id;
}


//// Storage


Storage::Storage(
        int load,
        std::string name,
        std::vector<std::string> skills,
        const Point &location,
        const Window &work_time,
        std::vector<Job> unassigned_jobs)
        : load(load), name(std::move(name)), skills(std::move(skills)),
          location(location), work_time(work_time), unassigned_jobs(std::move(unassigned_jobs)) {}

[[maybe_unused]] void Storage::print() const {
    printf("Storage: %s\n", name.c_str());
}


//// Courier


Courier::Courier(std::string name,
                 std::string profile,
                 const Cost &cost,
                 std::vector<int> value,
                 std::vector<std::string> skills,
                 int max_distance,
                 const Window &work_time,
                 const Point &start_location,
                 const Point &end_location)
        : name(std::move(name)), profile(std::move(profile)), cost(cost), value(std::move(value)),
          skills(std::move(skills)), max_distance(max_distance), work_time(work_time),
          start_location(start_location), end_location(end_location) {}

[[maybe_unused]] void Courier::print() const {
    printf("Courier; name: %s\n", name.c_str());
}

bool Courier::operator==(const Courier &other) const {
    return name == other.name;
}
