# https://adventofcode.com/2021/day/2

import os

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


# part 1
def calculate_position(input_file: str) -> (int, int):
    position = 0
    depth = 0

    with open(input_file) as f:
        for line in f:
            move, num = line.strip().split(maxsplit=1)

            if move == 'forward':
                position += int(num)
            elif move == 'up':
                depth -= int(num)
            elif move == 'down':
                depth += int(num)
            else:
                raise ValueError(f'Could not parse line: {line}')
    return position, depth


def test_calculate_position():
    test_final_position, test_final_depth = calculate_position(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_final_position == 15
    assert test_final_depth == 10


# part 2

def calculate_position2(input_file: str) -> (int, int):
    position = 0
    depth = 0
    aim = 0

    with open(input_file) as f:
        for line in f:
            move, num = line.strip().split(maxsplit=1)

            if move == 'forward':
                position += int(num)
                depth += int(num) * aim
            elif move == 'up':
                aim -= int(num)
            elif move == 'down':
                aim += int(num)
            else:
                raise ValueError(f'Could not parse line: {line}')

    return position, depth


def test_calculate_position2():
    test_position, test_depth = calculate_position2(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_position == 15
    assert test_depth == 60


if __name__ == "__main__":
    final_position, final_depth = calculate_position(INPUT_FILE)
    print(f'Horizontal position is {final_position}, depth is {final_depth}.\n'
          f'Your final position is thus {final_position * final_depth}')
    final_position2, final_depth2 = calculate_position2(INPUT_FILE)
    print(f'Horizontal position 2 is {final_position2}, depth 2 is {final_depth2}.\n'
          f'Your final position 2 is thus {final_position2 * final_depth2}')
