# https://adventofcode.com/2022/day/5

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()


def parse_stack(line: str) -> list:
    line = list(line)
    return line[1::4]


def parse_instructions(line: str) -> list:
    row = line.split(' ')
    return [int(number) for number in row[1::2]]


def parse_input(input_file: Path) -> (list[list[str]], list[list[int]]):
    data = input_file.read_text().splitlines()
    rows = []
    instructions = []
    for line in data:
        if '[' in line:
            rows.append(parse_stack(line))
        elif 'move' in line:
            instructions.append(parse_instructions(line))
        else:
            pass
    # transpose rows to columns, reverse each column and remove empty elements
    cols = []
    for col in zip(*rows):
        col = list(col)
        cols.append([c for c in col[::-1] if c != ' '])
    return cols, instructions


# part 1
def rearrange_crates(crates: list, instructions: list, direction: int = 1) -> str:
    for instruction in instructions:
        number_of_crates, origin, destination = instruction
        stack = crates[origin - 1][-number_of_crates:]
        crates[origin - 1][-number_of_crates:] = []
        crates[destination - 1] += stack[::direction]
    return ''.join(col[-1] for col in crates)


def test_rearrange_crates():
    test_stacks, test_instructions = parse_input(HERE / INPUT_TEST)
    test_top_crates = rearrange_crates(crates=test_stacks, instructions=test_instructions, direction=-1)
    assert test_top_crates == 'CMZ'


# part 2
def test_rearrange_more_crates():
    test_stacks, test_instructions = parse_input(HERE / INPUT_TEST)
    test_top_crates = rearrange_crates(crates=test_stacks, instructions=test_instructions)
    assert test_top_crates == 'MCD'


if __name__ == "__main__":
    stacks, instr = parse_input(HERE / INPUT_FILE)
    final_top_crates = rearrange_crates(crates=deepcopy(stacks), instructions=instr, direction=-1)
    print(f'The crates that end up on top of each stack are: {final_top_crates}.')

    final_top_crates2 = rearrange_crates(crates=stacks, instructions=instr)
    print(f'The crates that end up on top of each stack are: {final_top_crates2}.')
