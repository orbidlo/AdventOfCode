# https://adventofcode.com/2021/day/9

from timeit import default_timer as timer
from dataclasses import dataclass, field
from collections import namedtuple, defaultdict
from typing import Optional

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Point = namedtuple('Point', 'x y')

MAX_LVL = 9


@dataclass(frozen=False)
class Cave:
    _levels: list[list[int]]
    basins: defaultdict[Point, set[Point]] = field(init=False)

    def __post_init__(self):
        self.basins = defaultdict(set)

    def shape(self) -> tuple[int, int]:
        """ Shape of cave X x Y """
        return len(self._levels[0]), len(self._levels)

    def __getitem__(self, point: Point) -> int:
        return self._levels[point.y][point.x]

    def is_within_boundary(self, point: Point) -> bool:
        """ If given point exists within Caves boundary """
        width, height = self.shape()
        return (0 <= point.x < width) and (0 <= point.y < height)

    def get_adjacent(self, point: Point) -> Point:
        """ For given point generates adjacent points within Caves boundary. """
        left = Point(point.x - 1, point.y)
        right = Point(point.x + 1, point.y)
        up = Point(point.x, point.y - 1)
        down = Point(point.x, point.y + 1)

        for p in [up, right, down, left]:
            if self.is_within_boundary(p):
                yield p

    def is_lowest(self, point: Point) -> bool:
        """ If given point is lowest among all it's neighbors """
        return self[point] <= min(self[a] for a in self.get_adjacent(point))

    def is_in_basin(self, point: Point) -> Optional[Point]:
        """ If given points belongs to basin already, return it's lowest point """
        for key, val in self.basins.items():
            if point in val:
                return key
        return None

    def add_basin(self, lowest_point: Point):
        """ Create and populate basin for the given lowest point. """
        # skip this point if it is already in basin (basin has multiple lowest points)
        if not self.is_in_basin(lowest_point):
            queue = [lowest_point]
            while queue:
                point = queue.pop()
                # add point to basin
                self.basins[lowest_point].add(point)
                for adj in self.get_adjacent(point):
                    # skip top level point
                    if self[adj] >= MAX_LVL:
                        continue
                    # skip point already in basin or in queue
                    if self.is_in_basin(adj) or adj in queue:
                        continue
                    # add adjacent point to basin
                    queue.append(adj)


def parse_lines(input_file) -> list[list[int]]:
    lines = []
    with open(input_file) as f:
        for line in f:
            lines.append([int(x) for x in line.strip()])
    return lines


def get_lowest_levels(caves: Cave) -> list[Point]:
    """ Get risk level of all lowest points in Caves """
    levels = []
    for x in range(caves.shape()[0]):
        for y in range(caves.shape()[1]):
            p = Point(x, y)
            if caves.is_lowest(p):
                levels.append(p)

    return levels


def get_three_largest_basins_size(caves: Cave) -> list[int]:
    """ Get size of three largest basins. """
    # create basins for all lowest points
    for p in get_lowest_levels(caves):
        caves.add_basin(p)

    basins = list(caves.basins.values())
    basins.sort(key=len, reverse=True)

    return [len(b) for b in basins[0:3]]


# part 1
def get_risk_level(input_file: str) -> int:
    caves = Cave(parse_lines(input_file))
    return sum(caves[p] + 1 for p in get_lowest_levels(caves))


def test_get_risk_level():
    test_count = get_risk_level(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 15


# part 2
def get_basin_risk_level(input_file: str) -> int:
    caves = Cave(parse_lines(input_file))
    risk = 1
    for size in get_three_largest_basins_size(caves):
        risk *= size
    return risk


def test_get_three_largest_basins_size():
    test_size = get_basin_risk_level(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_size == 1134


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    total_sum = get_risk_level(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Sum of lowest risk levels is {total_sum}.')

    start = timer()
    total_size = get_basin_risk_level(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Three largest basins\' risk level is {total_size}.')
