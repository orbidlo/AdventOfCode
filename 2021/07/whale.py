# https://adventofcode.com/2021/day/7

from timeit import default_timer as timer
from statistics import median

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def parse_lines(input_file) -> list[int]:
    with open(input_file) as f:
        parsed = [int(x) for x in f.readline().strip().split(',')]
    return parsed


def get_simple_distance(a: int, b: int) -> int:
    return abs(a - b)


def get_distance(a: int, b: int) -> int:
    distance = get_simple_distance(a, b)
    return (distance * (distance + 1)) // 2


# part 1
def align_crabs(input_file: str) -> (int, int):
    positions = parse_lines(input_file)
    pos = median(positions)
    fuel = sum(get_simple_distance(pos, p) for p in positions)

    return int(pos), int(fuel)


def test_align_crabs():
    test_pos, test_fuel = align_crabs(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_pos == 2
    assert test_fuel == 37


# part 2
def align_crabs2(input_file: str) -> (int, int):
    positions = sorted(parse_lines(input_file))
    distances = []

    for candidate in range(positions[0], positions[-1]):
        distances.append(sum([get_distance(candidate, pos) for pos in positions]))
    # min_dis = math.floor(mean(positions))
    min_dis = min(distances)
    best_pos = distances.index(min_dis)

    return best_pos, min_dis


def test_align_crabs2():
    test_pos, test_fuel = align_crabs2(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_pos == 5
    assert test_fuel == 168


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    median_position, total_fuel = align_crabs(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Final median position is {median_position}. '
                 f'Total fuel spent to get there is {total_fuel}.')

    start = timer()
    best_position, total_fuel = align_crabs2(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.2f}s elapsed) Final best position is {best_position}. '
                 f'Total fuel spent to get there is {total_fuel}.')
