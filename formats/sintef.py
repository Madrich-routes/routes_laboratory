def parse_solution(filename: str):
    """
    Псарсим решение CVRPTW в формате cintef
    """
    cars = []
    with open(filename) as f:
        for l in f:
            if 'Route' in l:
                str_ids = l.split(':')[-1].strip().split()
                cars += [[int(i) for i in str_ids]]

    return cars
