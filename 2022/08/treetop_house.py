# https://adventofcode.com/2022/day/8

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps, cached_property
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()

SMALL_SIZE = 100000
DISK_SIZE = 70000000
TARGET_SIZE = 30000000


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, direction: Dirs):
        return Point(self.x + direction.value.x, self.y + direction.value.y)

    def __hash__(self):
        return hash((self.y, self.y))


class Dirs(Enum):
    UP = Point(0, -1)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)


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


@dataclass(frozen=False)
class Forest:
    _heights: list[list[int]]
    _visible: set[Point] = field(default_factory=set)

    @cached_property
    def width(self) -> int:
        return len(self._heights[0])

    @cached_property
    def height(self) -> int:
        return len(self._heights)

    def __getitem__(self, point: Point) -> int:
        return self._heights[point.y][point.x]

    def __setitem__(self, key: Point, value: int) -> None:
        self._heights[key.y][key.x] = value

    def __repr__(self) -> str:
        return '\n' + '\n'.join(str(row) for row in self._heights)

    def is_out_of_boundary(self, point: Point, direction: Dirs) -> bool:
        point = point + direction
        return (point.x < 0) or (point.x >= self.width) or (point.y < 0) or (point.y >= self.height)

    def calc_visibility(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                for direction in Dirs:
                    if self.is_visible_from_dir(Point(x, y), direction):
                        break

    def all_points_in_dir(self, point: Point, direction: Dirs):
        while not self.is_out_of_boundary(point, direction):
            new = point + direction
            yield new
            point = new

    def max_in_dir(self, point: Point, direction: Dirs) -> bool:
        for new in self.all_points_in_dir(point, direction):
            if self[point] <= self[new]:
                return False
        return True

    def is_visible_from_dir(self, point: Point, direction: Dirs) -> bool:
        if point in self._visible:
            return True
        if self.is_out_of_boundary(point, direction) or self.max_in_dir(point, direction):
            self._visible.add(point)
            return True
        return False

    def all_visible(self) -> set:
        self.calc_visibility()
        return self._visible

    def view_dist_in_dir(self, point: Point, direction: Dirs) -> int:
        count = 0
        for new in self.all_points_in_dir(point, direction):
            count += 1
            if self[point] <= self[new]:
                break
        return count

    def get_scenic_score(self, point: Point):
        return math.prod(self.view_dist_in_dir(point, direction) for direction in Dirs)


@timeit
def parse_input(input_file) -> list[list[int]]:
    lines = []
    with open(input_file) as file:
        for line in file:
            lines.append([int(x) for x in list(line.strip())])
    return lines


# part 1
@timeit
def find_visible_trees(forest: Forest) -> int:
    return len(forest.all_visible())


def test_find_visible_trees():
    data = parse_input(HERE / INPUT_TEST)
    forest = Forest(data)
    assert find_visible_trees(forest) == 21


# part 2
@timeit
def highest_scenic_score(forest: Forest) -> int:
    return max(forest.get_scenic_score(point) for point in forest.all_visible())


def test_highest_scenic_score():
    data = parse_input(HERE / INPUT_TEST)
    forest = Forest(data)
    assert highest_scenic_score(forest) == 8


def main():
    data = parse_input(HERE / INPUT_FILE)
    forest = Forest(data)

    visible_trees = find_visible_trees(forest)
    print(f'The number of visible trees in forest is {visible_trees}.')

    max_score = highest_scenic_score(forest)
    print(f'The highest scenic score in forest is {max_score}.')


if __name__ == "__main__":
    main()
