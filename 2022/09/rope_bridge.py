# https://adventofcode.com/2022/day/9

from __future__ import annotations

import time
import typing
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path

import pytest

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()

TEST_INPUT_1 = ['R 4', 'U 4', 'L 3', 'D 1', 'R 4', 'D 1', 'L 5', 'R 2']
TEST_INPUT_2 = ['R 5', 'U 8', 'L 8', 'D 3', 'R 17', 'D 10', 'L 25', 'U 20']

SMALL_ROPE = 2
LONG_ROPE = 10

DIRECTIONS = {
    'U': (0, -1),
    'R': (1, 0),
    'D': (0, 1),
    'L': (-1, 0),
}

Direction = typing.Tuple[int, int]


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        total_time = end_time - start_time
        print(f'\tFunction {func.__name__} took {total_time / 1000} μs')
        return result

    return timeit_wrapper


def cmp(a: int, b: int) -> int:
    # -1 when a<b, 0 when a==b, 1 when a>b
    return (a > b) - (a < b)


@dataclass(frozen=True)
class Knot:
    x: int
    y: int

    def __add__(self, other: Direction) -> Knot:
        return Knot(self.x + other[0], self.y + other[1])

    def follow(self, other: Knot) -> Knot:
        # previous knot is too far away
        if abs(self.x - other.x) >= 2 or abs(self.y - other.y) >= 2:
            x = self.x + cmp(other.x, self.x)
            y = self.y + cmp(other.y, self.y)
            return Knot(x, y)
        # previous knot is adjacent
        return self


@dataclass(frozen=False)
class Rope:
    length: int
    visited: set[Knot] = field(default_factory=set)
    _knots: list[Knot] = field(default_factory=list)

    @property
    def head(self) -> Knot:
        return self._knots[0]

    @property
    def tail(self) -> Knot:
        return self._knots[-1]

    def __post_init__(self):
        for idx in range(self.length):
            self._knots.append(Knot(0, 0))
        self.visited.add(Knot(0, 0))

    def move_head(self, direction: Direction) -> None:
        self._knots[0] = self.head + direction
        for idx in range(1, len(self._knots)):
            current = self._knots[idx]
            previous = self._knots[idx - 1]
            new = current.follow(previous)
            if new is current:
                # knot is adjacent and doesn't move
                return
            self._knots[idx] = new
        self.visited.add(self.tail)

    def run_instructions(self, instructions: list[tuple[Direction, int]]) -> None:
        for direction, times in instructions:
            for _ in range(times):
                self.move_head(direction)


@timeit
def parse_input(lines: list) -> list[tuple[Direction, int]]:
    parsed_lines = []
    for line in lines:
        direction, times = line.strip().split()
        parsed_lines.append((DIRECTIONS[direction], int(times)))
    return parsed_lines


# part 1
@timeit
def count_visited_by_tail(rope: Rope, instr: list[tuple[Direction, int]]) -> int:
    rope.run_instructions(instr)
    return len(rope.visited)


@pytest.mark.parametrize(
    "lines,length,expected", [
        (TEST_INPUT_1, SMALL_ROPE, 13),
        (TEST_INPUT_1, LONG_ROPE, 1),
        (TEST_INPUT_2, SMALL_ROPE, 88),
        (TEST_INPUT_2, LONG_ROPE, 36),
    ])
def test_count_visited_by_tail(lines, length, expected):
    instr = parse_input(lines)
    rope = Rope(length)
    visited = count_visited_by_tail(rope, instr)
    assert visited == expected


def main():
    input_file = HERE / INPUT_FILE
    lines = input_file.read_text().splitlines()
    instr = parse_input(lines)
    rope = Rope(SMALL_ROPE)
    visited = count_visited_by_tail(rope, instr)
    print(f'Number of positions visited by tail at {SMALL_ROPE} length after running instructions is {visited}.')

    long_rope = Rope(LONG_ROPE)
    visited = count_visited_by_tail(long_rope, instr)
    print(f'Number of positions visited by tail at {LONG_ROPE} length after running instructions is {visited}.')


if __name__ == "__main__":
    main()
