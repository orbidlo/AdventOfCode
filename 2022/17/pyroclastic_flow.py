# https://adventofcode.com/2022/day/17

from __future__ import annotations

import typing
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import cycle
from operator import attrgetter
from pathlib import Path

import pytest

from libs import timeit, INPUT_FILE, INPUT_TEST, Point, Dirs

HERE = Path(__file__).parent.resolve()
STEPS = 2022
IMPRESSIVE_STEPS = 1000000000000
GRID_WIDTH = 7

TO_DIR = {'<': Dirs.LEFT, '>': Dirs.RIGHT}

# X: →, Y: ↑
MINUS_PTS = {Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)}
PLUS_PTS = {Point(1, 0), Point(0, 1), Point(1, 1), Point(2, 1), Point(1, 2)}
CORNER_PTS = {Point(0, 0), Point(1, 0), Point(2, 0), Point(2, 1), Point(2, 2)}
PIPE_PTS = {Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3)}
BLOCK_PTS = {Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)}


@dataclass(frozen=False)
class Shape:
    name: str
    _points: set[Point]
    shift_x: int = 2
    shift_y: int = 3
    width: int = field(init=False)
    height: int = field(init=False)
    settled: bool = field(init=False)

    def __post_init__(self):
        self.height = max(self._points, key=attrgetter('y')).y + 1
        self.width = max(self._points, key=attrgetter('x')).x + 1
        self.settled = False

    def __add__(self, direction: Point) -> Shape:
        new_shape = deepcopy(self)
        new_shape.move(direction)
        return new_shape

    def move(self, direction: Point) -> None:
        self.shift_x += direction.x
        self.shift_y += direction.y

    def all_points(self, y_level: set[int] | int | None = None) -> typing.Iterator[Point]:
        if y_level is None:
            y_level = set(range(self.height))
        if isinstance(y_level, int):
            y_level = {y_level}
        yield from {Point(point.x + self.shift_x, point.y + self.shift_y)
                    for point in self._points if point.y in y_level}


SHAPES = [
    Shape('minus', MINUS_PTS),
    Shape('plus', PLUS_PTS),
    Shape('corner', CORNER_PTS),
    Shape('pipe', PIPE_PTS),
    Shape('block', BLOCK_PTS)

]


@dataclass
class Grid:
    _directions: list[Dirs]
    max_width: int = GRID_WIDTH
    settled_shapes: set[Point] = field(default_factory=set)
    settled_minus: set[Point] = field(default_factory=set)
    floor: list[int] = field(init=False)  # maximum height for each column in grid
    relative_shifts: list[tuple[int, ...]] = field(default_factory=list)
    minus_y: int = 0

    def __repr__(self) -> str:
        lines = []
        for y in range(self.height, -1, -1):
            line = '|'
            for x in range(self.max_width):
                point = Point(x, y)
                char = '.'
                if point in self.settled_shapes:
                    char = '#'
                if point in self.settled_minus:
                    char = '-'
                line += char
            lines.append(line + '|')
        lines.append('+' + '-' * self.max_width + '+\n')
        return '\n'.join(lines)

    def __post_init__(self) -> None:
        self.floor = [0] * self.max_width
        self.block_iter = cycle(SHAPES)
        self.direction_iter = cycle(self._directions)

    @property
    def height(self) -> int:
        if not self.settled_shapes:
            return 0
        # return max(self.floor)
        return max(self.settled_shapes, key=attrgetter('y')).y + 1

    def settle(self, shape: Shape):
        shape.settled = True
        if shape.name == 'minus':
            self.settled_minus.update(set(shape.all_points()))
        self.settled_shapes.update(set(shape.all_points()))

    def collides(self, shape: Shape) -> bool:
        # wall
        if (shape.shift_x < 0) or (shape.shift_x + shape.width > self.max_width):
            return True
        # floor
        if shape.shift_y < 0:
            return True
        # settled shapes
        for point in shape.all_points():
            if point in self.settled_shapes:
                return True
        return False

    def fall(self, shape: Shape):
        while not shape.settled:
            direction = next(self.direction_iter)
            old_x = shape.shift_x
            shape.move(direction.value)
            # wall collision
            if self.collides(shape):
                shape.shift_x = old_x
            old_y = shape.shift_y
            shape.move(Dirs.DOWN.value)
            # floor collision
            if self.collides(shape):
                shape.shift_y = old_y
                self.settle(shape)
                break


@timeit
def parse(input_file: Path) -> list[Dirs]:
    line = input_file.read_text().strip()
    directions = [TO_DIR[char] for char in line]
    return directions


# part 1
@timeit
def get_tower_height(steps: int, directions: list[Dirs]) -> int:
    grid = Grid(directions)
    shape_iter = cycle(SHAPES)

    for step in range(1, steps + 1):
        shape = next(shape_iter)
        shape = deepcopy(shape)
        shape.move(Point(0, grid.height))
        grid.fall(shape)
    return grid.height


@pytest.mark.parametrize(
    "steps,expected", [
        (STEPS, 3068),
        # (IMPRESSIVE_STEPS, 1514285714288)
    ])
def test_get_tower_height(steps, expected):
    input_file = HERE / INPUT_TEST
    directions = parse(input_file)
    height = get_tower_height(STEPS, directions)
    assert height == 3068


# part 2

def main():
    input_file = HERE / INPUT_FILE
    directions = parse(input_file)
    height = get_tower_height(STEPS, directions)
    print(f'Height of tower after {STEPS} blocks settled is:  {height} ')

    # height = get_tower_height(IMPRESSIVE_STEPS, directions)
    # print(f'Height of tower after {IMPRESSIVE_STEPS} blocks settled is:  {height} ')


if __name__ == "__main__":
    main()
