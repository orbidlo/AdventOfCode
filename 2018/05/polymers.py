# https://adventofcode.com/2018/day/5

import os.path
from operator import itemgetter

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def get_input(input_file):
    with open(input_file, "rb") as f:
        while True:
            # no need to read chunks as python already buffers input
            byte = f.read(1)
            if not byte:
                break
            yield (ord(byte))


def is_react(a: int, b: int):
    return abs(a - b) == 32


def react(input_file, filter_char=None):
    # initialise polymers by having starting item that is not going to react
    polymers = bytearray([255])
    if filter_char:
        iterator = filter(lambda x: x != filter_char and x != filter_char + 32, get_input(input_file))
    else:
        iterator = get_input(input_file)
    try:
        for b in iterator:
            # filter out unwanted polymers
            while is_react(polymers[-1], b):
                polymers.pop()
                b = next(iterator)
            polymers.append(b)
    except StopIteration:
        pass
    # skip dummy item
    return polymers[1:]


def test_react():
    result = react(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert result == b'dabCBAcaDA'


def optimize_react(input_file):
    results = {}
    # iterate over all letters and try removing them
    for filter_char in range(65, 91):
        results[filter_char] = len(react(input_file, filter_char))

    return min(results.items(), key=itemgetter(1))


def test_optimize_react():
    filtered, result = optimize_react(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert filtered == ord('C')
    assert result == 4


if __name__ == "__main__":
    print(f'Reacting polymers.... result is {len(react(INPUT_FILE))}')

    filtered, result = optimize_react(INPUT_FILE)
    print(f'Best result for filtering {chr(filtered)} is {result}')
