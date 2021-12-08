# https://adventofcode.com/2021/day/8

from timeit import default_timer as timer

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

UQ_SEGMENTS = {
    2: 1,
    4: 4,
    3: 7,
    7: 8
}

SEGMENTS = [
    (1, 1, 1, 0, 1, 1, 1),  # 0 - 6
    (0, 0, 1, 0, 0, 1, 0),  # 1 - 2
    (1, 0, 1, 1, 1, 0, 1),  # 2 - 5
    (1, 0, 1, 1, 0, 1, 1),  # 3 - 5
    (0, 1, 1, 1, 0, 1, 0),  # 4 - 4
    (1, 1, 0, 1, 0, 1, 1),  # 5 - 5
    (1, 1, 0, 1, 1, 1, 1),  # 6 - 6
    (1, 0, 1, 0, 0, 1, 0),  # 7 - 3
    (1, 1, 1, 1, 1, 1, 1),  # 8 - 7
    (1, 1, 1, 1, 0, 1, 1),  # 9 - 6
]


class Display:
    """ Represents 7-bit display. """
    bits: list[set[str]]  # bits contain all possible wires connected to each big

    def __init__(self):
        """ Initiate with all bits set to all possible wires """
        self.wiring = None
        self.bits = []
        for _ in range(7):
            self.bits.append(set('abcdefg'))

    def specify(self, bit: int, wire: str):
        """ For specific bit set exactly one wire connected to it and remove it from other bits. """
        assert len(wire) == 1, "Wire must be one letter."
        for options in self.bits:
            options.discard(wire)
        self.bits[bit] = {wire}

    def set_for_number(self, number_def: tuple[int, ...], wires: set[str]):
        """ Based on number bit definition set display bits from given wires """
        for bit_idx, bit_is_set in enumerate(number_def):
            option = self.bits[bit_idx]
            if not bit_is_set:
                # for disabled bits remove given wires
                option -= wires
            else:
                # for enabled bits add intersection of existing and given wires
                option &= wires

    def is_unambiguous(self) -> bool:
        """ Display is solved, we have exactly 1 wire for each bit """
        solved = all(len(options) == 1 for options in self.bits)
        if solved:
            self.wiring = [next(iter(options)) for options in self.bits]
        return solved

    def identify_digit(self, wires: set[str]) -> int:
        """ From given wires identify number from display bits and number definition. """
        assert self.is_unambiguous(), 'Cannot identify until we solve all bits from input.'

        digit_by_letters = tuple(
            1 if wire in wires else 0
            for wire in self.wiring
        )
        return SEGMENTS.index(digit_by_letters)  # type: ignore


def parse_wires(input_str: str) -> list[set[str]]:
    return [set(item) for item in input_str.strip().split()]


def parse_lines(input_file) -> list[tuple[list[set[str]], list[set[str]]]]:
    lines = []
    with open(input_file) as f:
        for line in f:
            input_digits, output_digits = line.strip().split(' | ')
            lines.append((parse_wires(input_digits), parse_wires(output_digits)))
    return lines


# part 1
def count_unique_segments(input_file: str) -> int:
    lines = parse_lines(input_file)
    counter = 0
    for _, outputs in lines:
        counter += len([len(d) for d in outputs if len(d) in UQ_SEGMENTS])

    return counter


def resolve(line: tuple[list[set[str]], list[set[str]]]) -> int:
    inputs, outputs = line
    display = Display()
    inputs.sort(key=len)

    display.set_for_number(SEGMENTS[1], inputs[0])
    display.set_for_number(SEGMENTS[7], inputs[1])
    display.set_for_number(SEGMENTS[4], inputs[2])
    display.set_for_number(SEGMENTS[8], inputs[-1])

    seven = inputs[1]
    fives = [i for i in inputs if len(i) == 5]
    for candidate in fives:
        if seven <= candidate:
            # three is only 5-letter long candidate that contains seven's bits
            display.set_for_number(SEGMENTS[3], candidate)

    almost_two = set()
    for bit in (0, 3, 4, 6):  # all bits but second for number two
        almost_two |= display.bits[bit]

    for candidate in fives:
        if almost_two <= candidate:
            remaining_wires = candidate - almost_two  # get missing wire for 2nd bit
            assert len(remaining_wires) == 1
            remaining_wire = remaining_wires.pop()
            display.specify(bit=2, wire=remaining_wire)

    number = 0
    for output in outputs:
        number = number * 10 + display.identify_digit(output)

    return number


def sum_numbers(input_file) -> int:
    lines = parse_lines(input_file)
    s = 0
    for line in lines:
        s += resolve(line)
    return s


def test_count_unique_segments():
    test_count = count_unique_segments(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 26


def test_sum_numbers():
    test_sum = sum_numbers(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_sum == 61229


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    total_count = count_unique_segments(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) There is {total_count} unique segment numbers.')

    start = timer()
    total_sum = sum_numbers(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) There is {total_sum} of all parsed numbers.')
