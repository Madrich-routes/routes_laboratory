#include "generators.h"

float generate_value() {
    std::random_device rd;
    std::mt19937 mersenne(rd());
    return static_cast<float>(mersenne()) / static_cast<float>(UINT32_MAX);
}

std::tuple<float, float> generate_tuple() {
    return std::tuple<float, float>(generate_value(), generate_value());
}

std::vector<std::tuple<float, float>> generate_points(int n, float min_x, float max_x, float min_y, float max_y) {
    float diff_x = max_x - min_x;
    float diff_y = max_y - min_y;
    std::vector ret = std::vector<std::tuple<float, float>>(n);
    for (auto &point : ret) {
        auto[x, y] = generate_tuple();
        x = x * diff_x + min_x;
        y = y * diff_y + min_y;
        point = std::tuple(x, y);
    }
    return ret;
}

std::vector<std::vector<int>>
generate_matrix(const std::vector<std::tuple<float, float>> &points, const std::string &type) {
    double c = (type == "distance" ? 9.67 : 1.3);
    std::size_t size = points.size();
    std::vector<std::vector<int>> matrix(size, std::vector<int>(size, 0));
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            auto[first_x, first_y] = points[i];
            auto[second_x, second_y] = points[j];
            double value = sqrt(pow((second_x - first_x), 2) + pow((second_y - second_x), 2));
            matrix[i][j] = static_cast<int>((value * (generate_value() / 2) + value) * c * 1e4);
            matrix[j][i] = static_cast<int>((value * (generate_value() / 2) + value) * c * 1e4);
        }
    }
    return matrix;
}

std::vector<Job>
generate_jobs(const std::vector<Point> &points, int start, int end, const std::string &storage_id) {
    int size = end - start;
    std::vector jobs = std::vector<Job>(size);
    for (int i = 0; i < size; ++i) {
        std::ostringstream start_t;
        std::ostringstream end_t;
        start_t << "2020-10-01T" << 10 + (i % 4) << ":00:00Z";
        end_t << "2020-10-01T" << 12 + (i % 5) << ":00:00Z";
        Window window = Window(start_t.str(), end_t.str());
        jobs[i] = Job(300, "", {1, 2}, {"brains"}, points[i + start], {window});
    }
    return jobs;
}

std::tuple<int, std::vector<Courier>, Storage, std::map<std::string, Matrix>>
generate_vrp(int jobs, int couriers) {
    int size = 1 + jobs + couriers;
    std::vector pts = generate_points(size, 55.7, 55.8, 37.6, 37.7);
    std::vector distance = generate_matrix(pts, "distance");
    std::vector travel_time = generate_matrix(pts, "travel_time");
    Matrix matrix("driver", distance, travel_time);
    std::map<std::string, Matrix> ret_matrix = {{"driver", matrix}};

    std::vector<Point> points(size);
    for (int i = 0; i < size; ++i) {
        points[i] = Point(i, pts[i]);
    }

    Window window = Window("2020-10-01T10:00:00Z", "2020-10-01T20:00:00Z");
    Storage storage(300, "storage", {"brains"}, points[0], window, generate_jobs(points, 1, 1 + jobs, "storage"));

    std::vector<Courier> couriers_list(couriers);
    for (int i = 0; i < couriers; ++i) {
        Point courier_loc = points[1 + jobs + i];
        std::string name = "courier_" + std::to_string(i);
        Cost cost = Cost(10., 0.5, 1.2);
        couriers_list[i] = Courier(name, "driver", cost, {40, 80}, {"brains"}, 1e6, window, courier_loc, courier_loc);
    }
    return {2, couriers_list, storage, ret_matrix};
}
