# https://adventofcode.com/2022/day/24

from __future__ import annotations

import typing
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pytest

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()


class Point(typing.NamedTuple):
    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)


class Dirs(Enum):
    DOWN = Point(0, 1)
    UP = Point(0, -1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)
    STAY = Point(0, 0)


TO_DIR = {
    '<': Dirs.LEFT,
    '>': Dirs.RIGHT,
    '^': Dirs.UP,
    'v': Dirs.DOWN
}

DirQueue = list[deque[bool]]


@dataclass
class Grid:
    blizzard: dict[Dirs, DirQueue]
    start: Point
    end: Point
    # viable positions for expedition in current blizzard condition
    expedition: set[Point] = field(default_factory=set)
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self) -> None:
        self.expedition.add(self.start)
        self.width = len(self.blizzard[Dirs.UP])
        self.height = len(self.blizzard[Dirs.LEFT])

    def __repr__(self) -> str:
        lines = []
        for y in range(-1, self.height + 1):
            line = ''
            for x in range(-1, self.width + 1):
                point = Point(x, y)
                char = self[point]
                if len(char) > 1:
                    char = str(len(char))
                line += char
            lines.append(line)
        return '\n'.join(lines)

    def __getitem__(self, point: Point) -> str:
        if self.is_wall(point):
            return '#'
        if self.start == point or self.end == point:
            if point in self.expedition:
                return 'E'
            return '.'
        left = self.blizzard[Dirs.LEFT][point.y][point.x]
        right = self.blizzard[Dirs.RIGHT][point.y][point.x]
        up = self.blizzard[Dirs.UP][point.x][point.y]
        down = self.blizzard[Dirs.DOWN][point.x][point.y]
        result = ''
        if left:
            result += '<'
        if right:
            result += '>'
        if up:
            result += '^'
        if down:
            result += 'v'
        if not result:
            if point in self.expedition:
                return 'E'
            return '.'
        return result

    def is_blizzard(self, pos: Point) -> bool:
        """ Given position contains blizzard. """
        return (
                self.blizzard[Dirs.LEFT][pos.y][pos.x] or
                self.blizzard[Dirs.RIGHT][pos.y][pos.x] or
                self.blizzard[Dirs.UP][pos.x][pos.y] or
                self.blizzard[Dirs.DOWN][pos.x][pos.y]
        )

    def is_wall(self, pos: Point) -> bool:
        """ Given position is in grid wall. """
        # wall is not start or end
        if pos == self.start or pos == self.end:
            return False
        # wall is not some tile in grid
        if (0 <= pos.x < self.width) and (0 <= pos.y < self.height):
            return False
        # everything else is
        return True

    def is_free(self, pos: Point) -> bool:
        """ Given position is free and can be moved into by expedition. """
        # start & end are always free since blizzard can never go there
        if pos == self.start or pos == self.end:
            return True
        # wall is never free
        if self.is_wall(pos):
            return False
        # blizzard is never free
        if self.is_blizzard(pos):
            return False
        # everything else is
        return True

    def move_blizzard(self) -> None:
        """ Move blizzard (wrapped) in all 4 directions. """
        for y in range(self.height):
            self.blizzard[Dirs.LEFT][y].rotate(-1)
            self.blizzard[Dirs.RIGHT][y].rotate(1)
        for x in range(self.width):
            self.blizzard[Dirs.UP][x].rotate(-1)
            self.blizzard[Dirs.DOWN][x].rotate(1)

    def move_expedition(self) -> None:
        """ Move expedition in all possible directions that don't contain blizzard (BFS)."""
        new_expedition = set()
        moved = set()
        for current in self.expedition:
            for direction in Dirs:
                new = current + direction.value
                if new in moved:
                    continue
                if self.is_free(new):
                    new_expedition.add(new)
                moved.add(new)
        self.expedition = new_expedition

    def is_end(self) -> bool:
        return self.end in self.expedition


@timeit
def parse(input_file: Path) -> Grid:
    data = input_file.read_text().splitlines()
    width = len(data[0]) - 2
    height = len(data) - 2
    lines = {
        Dirs.LEFT: [deque([False] * width) for _ in range(height)],
        Dirs.RIGHT: [deque([False] * width) for _ in range(height)],
        Dirs.UP: [deque([False] * height) for _ in range(width)],
        Dirs.DOWN: [deque([False] * height) for _ in range(width)]
    }
    for y, line in enumerate(data[1:-1]):
        for x, char in enumerate(line[1:-1]):
            assert char != '#'
            if char == '.':
                continue
            assert char in TO_DIR.keys()
            if TO_DIR[char] == Dirs.LEFT:
                lines[Dirs.LEFT][y][x] = True
            if TO_DIR[char] == Dirs.RIGHT:
                lines[Dirs.RIGHT][y][x] = True
            if TO_DIR[char] == Dirs.UP:
                lines[Dirs.UP][x][y] = True
            if TO_DIR[char] == Dirs.DOWN:
                lines[Dirs.DOWN][x][y] = True
    grid = Grid(lines, start=Point(0, -1), end=Point(width - 1, height))
    return grid


# Part 1 & 2
@timeit
def get_best_path(grid: Grid, steps: int) -> int:
    counter = 0
    start = grid.start
    end = grid.end
    goal = [(start, end) if not (step % 2) else (end, start) for step in range(steps)]
    for times, (start, end) in enumerate(goal, 1):
        # reset expedition position within map for given start+end but keep blizzard state
        grid = Grid(grid.blizzard, start, end)
        while not grid.is_end():
            grid.move_blizzard()
            grid.move_expedition()
            counter += 1
        if steps == times:
            return counter


@pytest.mark.parametrize(
    "steps,expected", [
        (1, 18),
        (3, 54),
    ])
def test_get_best_path_back_and_again(steps, expected):
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    answer = get_best_path(grid, steps)
    assert answer == expected


def main():
    input_file = HERE / INPUT_FILE
    grid = parse(input_file)
    answer = get_best_path(grid, 1)
    print(f'Shortest path to end while avoiding blizzards is {answer}')
    grid = parse(input_file)
    answer = get_best_path(grid, 3)
    print(f'Shortest path to end, back and to end again while avoiding blizzards is {answer}')


if __name__ == "__main__":
    main()
