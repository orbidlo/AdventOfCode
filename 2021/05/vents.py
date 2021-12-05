# https://adventofcode.com/2021/day/5

from __future__ import annotations

import sys
from dataclasses import dataclass
from collections import Counter, namedtuple

import os
import itertools
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Point = namedtuple('Point', ['x', 'y'])


def parse_point(point_str: str) -> Point:
    x, y = point_str.split(sep=',')
    return Point(int(x), int(y))


@dataclass
class Line:
    a: Point
    b: Point

    def get_points(self) -> list[Point]:
        """ Calculate all points that line goes through """
        incr_x = 1 if self.a.x <= self.b.x else -1
        incr_y = 1 if self.a.y <= self.b.y else -1

        x_coords = list(range(self.a.x, self.b.x + incr_x, incr_x))
        y_coords = list(range(self.a.y, self.b.y + incr_y, incr_y))

        if self.is_vertical():
            fill = self.a.x
        elif self.is_horizontal():
            fill = self.a.y
        else:  # line is diagonal -> fill is not needed
            fill = None

        # create points from x,y coordinates
        # for non-diagonal lines the coords are not of same length and the shorter list must be filled
        all_points = [Point(x, y) for x, y in itertools.zip_longest(x_coords, y_coords, fillvalue=fill)]

        return all_points

    def is_vertical(self) -> bool:
        return self.a.x == self.b.x

    def is_horizontal(self) -> bool:
        return self.a.y == self.b.y

    def is_intersect(self, line: Line) -> set[Point]:
        """ Get set of all intersecting points """
        return set(self.get_points()) & set(line.get_points())


def parse_lines(input_file) -> list[Line]:
    # 0,9 -> 5,9  ... [(0,9),(5,9)]
    lines = []
    with open(input_file) as f:
        for row in f:
            a, b = row.strip().split(sep=' -> ')
            line = Line(parse_point(a), parse_point(b))
            lines.append(line)
    return lines


# part 1
def count_intersections(input_file: str, use_diagonal: bool = False) -> int:
    """ Count all points where at least two lines intersected. """
    lines = parse_lines(input_file)
    # filter out diagonal lines if needed
    if not use_diagonal:
        lines = [line for line in lines if line.is_vertical() or line.is_horizontal()]

    all_points = [line.get_points() for line in lines]

    # count all points generated from lines
    counter = Counter(itertools.chain.from_iterable(all_points))
    # if any point is generated more than once, it is intersection
    return sum(value > 1 for value in counter.values())


def test_count_intersections():
    test_count = count_intersections(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 5


def test_count_intersections_diagonal():
    test_count = count_intersections(os.path.join(os.path.dirname(__file__), INPUT_TEST), use_diagonal=True)
    assert test_count == 12


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    intersection_count = count_intersections(INPUT_FILE)
    logging.info(f'Your count of non-diagonal intersections is {intersection_count}.')

    intersection_diagonal_count = count_intersections(INPUT_FILE, use_diagonal=True)
    logging.info(f'Your count of all intersections is {intersection_diagonal_count}.')
