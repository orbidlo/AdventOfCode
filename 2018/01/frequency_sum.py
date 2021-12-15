# https://adventofcode.com/2018/day/1

from itertools import accumulate
import os.path

STARTING_FREQUENCY = 0
INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def list_forever(lst):
    while True:
        yield from lst


def get_frequency_list(input_file):
    with open(input_file) as f:
        frequency_list = list(map(int, f))
    return frequency_list


# part 1
def get_frequency(input_file):
    frequency_list = get_frequency_list(input_file)
    return len(list(frequency_list)), sum(frequency_list)


def test_get_frequency():
    test_count, test_result = get_frequency(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 4
    assert test_result == 3


# part 2
def get_repeat_frequency(input_file):
    frequency_list = get_frequency_list(input_file)
    duplicate_found = None
    found_frequencies = {STARTING_FREQUENCY}
    candidates = list_forever(frequency_list)

    for frequency in accumulate(candidates):
        if frequency in found_frequencies:
            duplicate_found = frequency
            break
        else:
            found_frequencies.add(frequency)

    return duplicate_found


def test_get_repeat_frequency():
    result = get_repeat_frequency(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert result == 2


if __name__ == "__main__":
    count, final_frequency = get_frequency(INPUT_FILE)
    print(f'Sum of frequency for {count} numbers is {final_frequency}')

    duplicate_frequency = get_repeat_frequency(INPUT_FILE)
    print(f'Duplicate frequency is {duplicate_frequency}')
