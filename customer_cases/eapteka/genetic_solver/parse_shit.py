import ujson


def parse_shit(shit: str):
    with open(shit, 'r') as f:
        solutions = ujson.load(f)
    for solution in solutions:
        print(solution)


parse_shit('./data/answer.json')
