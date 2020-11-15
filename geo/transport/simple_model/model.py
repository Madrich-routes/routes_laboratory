def download_transport_simple(file, points: list):

    p_dist, p_time = osrm_module.get_osrm_matrix(points, transport='foot')
    c_dist, c_time = osrm_module.get_osrm_matrix(points, transport='car')

    res_time = np.zeros(p_dist.shape)
    res_dist = np.zeros(p_dist.shape)

    res_time[p_time <= 15 * 60] = p_time[p_time <= res_time['time']]
    res_time[15 * 60 < p_time < 45 * 60] = p_time[15 * 60 < p_time < 45 * 60]

    travel_times, distances = [], []
    for i in range(len(points)):
        for j in range(len(points)):
            pt = p_dist[i][j]
            dtt, dd = return_checked(p_time[i][j], p_time[i][j])

            if pt <= 15 * 60:
                travel_times.append(int(pt))
                distances.append(int(pt))
            elif 15 * 60 < pt < 45 * 60:
                tt = int(min(dtt * 1.5, pt))
                travel_times.append(tt)
                distances.append(int(dd))
            else:
                tt = int(min(dtt * 2, pt))
                travel_times.append(tt)
                distances.append(int(dd))

    routing = {'profile': 'transport_simple', 'travelTimes': travel_times, 'distances': distances}

    with open(file, 'w') as f:
        ujson.dump(routing, f)
