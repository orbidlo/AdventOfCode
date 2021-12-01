# https://adventofcode.com/2021/day/1

import itertools
import os

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def is_greater_pairwise(iterable):
    itr_a, itr_b = itertools.tee(iterable)
    next(itr_b, None)
    return [y > x for (x, y) in zip(itr_a, itr_b)]


def is_greater_window(iterable):
    itr_a, itr_b, itr_c = itertools.tee(iterable, 3)
    next(itr_b, None)
    next(itr_c, None)
    next(itr_c, None)

    windows = zip(itr_a, itr_b, itr_c)
    sums = [sum(x) for x in windows]
    return is_greater_pairwise(sums)


def get_measurement_list(input_file):
    with open(input_file) as f:
        measurements = list(map(int, f))
    return measurements


# part 1
def count_increased_depth(input_file):
    measurements = get_measurement_list(input_file)
    truth_list = is_greater_pairwise(measurements)

    return sum(truth_list)


def test_count_increased_depth():
    test_count = count_increased_depth(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 7


# part 2
def count_increased_window_depth(input_file):
    measurements = get_measurement_list(input_file)
    truth_list = is_greater_window(measurements)

    return sum(truth_list)


def test_count_increased_window_depth():
    test_count = count_increased_window_depth(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 5


if __name__ == "__main__":
    count = count_increased_depth(INPUT_FILE)
    print(f'Sum of all measurements that were larger than previous one is {count}.')

    windows_count = count_increased_window_depth(INPUT_FILE)
    print(f'Sum of all measurement windows that were larger than previous one is {windows_count}.')
