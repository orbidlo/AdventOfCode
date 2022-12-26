# https://adventofcode.com/2022/day/23

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from enum import Enum
from itertools import cycle
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, Range

HERE = Path(__file__).parent.resolve()
STEPS = 10

# optimisation instead of using big dataclass
Point = tuple[int, int]


def add_points(a: Point, b: Point) -> Point:
    return a[0] + b[0], a[1] + b[1]


def sub_points(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


class Direction(Enum):
    N = (0, -1)
    NE = (1, -1)
    E = (1, 0)
    SE = (1, 1)
    S = (0, 1)
    SW = (-1, 1)
    W = (-1, 0)
    NW = (-1, -1)


class DirInt(Enum):
    N = 0
    S = 1
    W = 2
    E = 3


ADJACENT = [
    (Direction.N, Direction.NE, Direction.NW),
    (Direction.S, Direction.SE, Direction.SW),
    (Direction.W, Direction.NW, Direction.SW),
    (Direction.E, Direction.NE, Direction.SE)
]


def get_dirs_from(start: DirInt):
    num_dirs = len(DirInt)
    for i in range(num_dirs):
        yield DirInt((start.value + i) % num_dirs)


@dataclass
class Grid:
    elves: set[Point]
    candidates: dict[Point, Direction | None] = field(default_factory=dict)
    _directions: typing.Iterator[DirInt] = field(init=False)

    def __repr__(self) -> str:
        lines = []
        for y in self.height_range:
            line = ''
            for x in self.width_range:
                point = (x, y)
                char = '.'
                if point in self.elves:
                    char = '#'
                line += char
            lines.append(line)
        return '\n'.join(lines)

    def __post_init__(self) -> None:
        self._directions = cycle(d for d in DirInt)

    @property
    def height_range(self) -> Range:
        y_coords = {point[1] for point in self.elves}
        return Range(min(y_coords), max(y_coords))

    @property
    def width_range(self) -> Range:
        x_coords = {point[0] for point in self.elves}
        return Range(min(x_coords), max(x_coords))

    @property
    def empty_count(self) -> int:
        size = len(self.height_range) * len(self.width_range)
        return size - len(self.elves)

    def can_move_in_dir(self, point: Point, direction: DirInt) -> bool:
        for candidate in (add_points(point, d.value) for d in ADJACENT[direction.value]):
            if candidate in self.elves:
                return False
        return True

    def is_alone(self, elf: Point) -> bool:
        for direction in Direction:
            if add_points(elf, direction.value) in self.elves:
                return False
        return True

    def move(self) -> int:
        first_dir = next(self._directions)
        changes = 0
        dir_order = list(get_dirs_from(first_dir))
        for elf in self.elves:
            # don't move if there are no elves nearby
            if self.is_alone(elf):
                continue
            # for each direction starting from current one
            for d in dir_order:
                # check if the direction and its adjacent directions are empty
                if self.can_move_in_dir(elf, d):
                    direction = Direction[d.name]
                    # add new candidate for elf movement
                    candidate = add_points(elf, direction.value)
                    if candidate in self.candidates:
                        # we already have another elf who wants to move here! -> invalidate
                        self.candidates[candidate] = None
                    else:
                        self.candidates[candidate] = direction
                    break
        for candidate, d in self.candidates.items():
            # only one elf wanted to move to this position
            if d is None:
                continue
            elf = sub_points(candidate, d.value)
            self.elves.discard(elf)
            self.elves.add(candidate)
            changes += 1
        self.candidates.clear()
        return changes


@timeit
def parse(input_file: Path) -> Grid:
    data = input_file.read_text().splitlines()
    elves = set()
    y = 0
    for line in data:
        elves.update(set((x, y) for x, char in enumerate(line) if char == '#'))
        y += 1
    grid = Grid(elves)
    return grid


# part 1
@timeit
def count_empty_tiles(grid: Grid, steps: int) -> int:
    for _ in range(steps):
        grid.move()
    return grid.empty_count


def test_get_final_password():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    answer = count_empty_tiles(grid, STEPS)
    assert answer == 110


# Part 2
@timeit
def rounds_until_done(grid: Grid) -> int:
    step = 1
    while True:
        changes = grid.move()
        if not changes:
            break
        step += 1
    return step


def test_rounds_until_done():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    answer = rounds_until_done(grid)
    assert answer == 20


def main():
    input_file = HERE / INPUT_FILE
    grid = parse(input_file)
    answer = count_empty_tiles(grid, STEPS)
    print(f'Smallest rectangle containing all elves has {answer} empty tiles.')

    grid = parse(input_file)
    answer = rounds_until_done(grid)
    print(f'Number of rounds that must happen before all elves stop moving is {answer}')


if __name__ == "__main__":
    main()
