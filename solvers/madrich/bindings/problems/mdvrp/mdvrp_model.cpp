#include "mdvrp_model.h"


MdvrpRoute::MdvrpRoute(int vec,
                       int start_time,
                       const Courier &courier,
                       const Matrix &matrix,
                       std::vector<Track> tracks,
                       const State &state)
        : vec(vec), start_time(start_time), courier(courier), matrix(matrix),
          tracks(std::move(tracks)), state(state) {}

void MdvrpRoute::print() const {
    printf("Route; courier: %s, tracks: %llu, jobs: %d", courier.name.c_str(), tracks.size(), assigned_jobs());
}

int MdvrpRoute::assigned_jobs() const {
    int t = 0;
    for (const auto &track : tracks) {
        t += track.jobs.size();
    }
    return t;
}


[[maybe_unused]] void Track::print() const {
    printf("Track; storage: %s, jobs: %llu", storage.name.c_str(), jobs.size());
}

MdvrpTour::MdvrpTour(std::vector<Storage> storages) : storages(std::move(storages)) {}
