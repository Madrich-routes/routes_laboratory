#include "vrp/vrp_model.h"


/// VrpRoute

VrpRoute::VrpRoute(int vec,
                   int start_time,
                   const Storage &storage,
                   const Courier &courier,
                   const Matrix &matrix,
                   std::vector<Job> jobs,
                   const State &state)
        : vec(vec), storage(storage), courier(courier), matrix(matrix),
          start_time(start_time), jobs(std::move(jobs)), state(state) {}

[[maybe_unused]] void VrpRoute::print() const {
    printf("VrpRoute; courier: %s, jobs: %llu\n", courier.name.c_str(), jobs.size());
}

//// VrpTour

VrpTour::VrpTour(const Storage &storage)
        : storage(storage), routes(std::vector<VrpRoute>()) {}

[[maybe_unused]] void VrpTour::print() const {
    printf("VrpTour; storage: %s\n", storage.name.c_str());
}


State VrpTour::get_state() {
    State state = State();
    for (const auto &route : routes) {
        state += route.state;
    }
    return state;
}
