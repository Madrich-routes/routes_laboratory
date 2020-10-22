#include "vrp/vrp_model.h"


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

[[maybe_unused]] [[noreturn]] void Storage::print() const {
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

[[maybe_unused]] [[noreturn]] void Courier::print() const {
    printf("Courier; name: %s\n", name.c_str());
}

bool Courier::operator==(const Courier &other) const {
    return name == other.name;
}


/// Route

Route::Route(int vec,
             int start_time,
             const Storage &storage,
             const Courier &courier,
             const Matrix &matrix,
             std::vector<Job> jobs,
             const State &state)
        : vec(vec), storage(storage), courier(courier), matrix(matrix),
          start_time(start_time), jobs(std::move(jobs)), state(state) {}

[[maybe_unused]] [[noreturn]] void Route::print() const {
    printf("Route; courier: %s, jobs: %llu\n", courier.name.c_str(), jobs.size());
}

int Route::length() const {
    return jobs.size();
}

//// Tour

Tour::Tour(const Storage &storage)
        : storage(storage), routes(std::vector<Route>()) {}

[[maybe_unused]] [[noreturn]] void Tour::print() const {
    printf("Tour; storage: %s\n", storage.name.c_str());
}


State Tour::get_state() {
    State state = State();
    for (const auto &route : routes) {
        state += route.state;
    }
    return state;
}
