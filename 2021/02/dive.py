# https://adventofcode.com/2021/day/2

import os
import re

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


# part 1
def calculate_position(input_file):
    # code
    position = 0
    depth = 0

    pat = re.compile(r'(\w+) (\d+)')

    with open(input_file) as f:
        lines = f.readlines()

        for line in lines:
            if not line:
                break

            line = line.rstrip()
            result = pat.match(line)
            move = result.group(1)
            num = int(result.group(2))

            if move == 'forward':
                position += num
            elif move == 'up':
                depth -= num
            elif move == 'down':
                depth += num
    return position, depth


def test_calculate_position():
    test_final_horizontal_pos, test_final_depth = calculate_position(
        os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_final_horizontal_pos == 15
    assert test_final_depth == 10


# part 2

def calculate_position2(input_file):
    # code
    position = 0
    depth = 0
    aim = 0

    pat = re.compile(r'(\w+) (\d+)')

    with open(input_file) as f:
        lines = f.readlines()

        for line in lines:
            if not line:
                break

            line = line.rstrip()
            result = pat.match(line)
            move = result.group(1)
            num = int(result.group(2))

            if move == 'forward':
                position += num
                depth += num * aim
            elif move == 'up':
                aim -= num
            elif move == 'down':
                aim += num

    return position, depth


def test_calculate_position2():
    test_horizontal_pos, test_depth = calculate_position2(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_horizontal_pos == 15
    assert test_depth == 60


if __name__ == "__main__":
    # final_horizontal_pos, final_depth = calculate_position(INPUT_FILE, )
    final_horizontal_pos, final_depth = calculate_position2(INPUT_FILE, )
    print(f'Horizontal position is {final_horizontal_pos}, depth is {final_depth}.\n'
          f'Your final position is thus {final_horizontal_pos*final_depth}')
