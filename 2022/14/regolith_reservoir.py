# https://adventofcode.com/2022/day/14

from __future__ import annotations

import typing
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cached_property
from itertools import zip_longest
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __lt__(self, other: Point) -> bool:
        if self.x < other.x:
            return True
        if self.x > other.x:
            return False
        if self.x == other.x:
            return self.y < other.y

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)


DIRS = [Point(0, 1), Point(-1, 1), Point(1, 1)]
SAND_POINT = Point(500, 0)


def parse_point(point_str: str) -> Point:
    x, y = point_str.split(sep=',')
    return Point(int(x), int(y))


@dataclass
class Line:
    a: Point
    b: Point

    def __iter__(self) -> typing.Iterator[Point]:
        """ Generate all points that line goes through in sorted order. """
        a, b = self.get_start_end()
        if self.is_vertical():
            fill = self.a.x
        elif self.is_horizontal():
            fill = self.a.y
        else:  # line is diagonal -> fill is not needed
            fill = None
        # create points from x,y coordinates
        # for non-diagonal lines the coords are not of same length and the shorter list must be filled
        for x, y in zip_longest(range(a.x, b.x + 1), range(a.y, b.y + 1), fillvalue=fill):
            yield Point(x, y)

    def get_start_end(self) -> tuple[Point, Point]:
        if self.a < self.b:
            return self.a, self.b
        return self.b, self.a

    def is_vertical(self) -> bool:
        return self.a.x == self.b.x

    def is_horizontal(self) -> bool:
        return self.a.y == self.b.y


@dataclass
class Cavern:
    sand_origin: Point
    paths: list[Line] = field(default_factory=list)
    _sand: set[Point] = field(default_factory=set)
    _rocks: set[Point] = field(default_factory=set)
    floor_coeff: int | None = None

    def __repr__(self) -> str:
        x_coords = {point.x for point in self.all_path_borders()}
        x_coords.update({sand.x for sand in self._sand})
        y_coords = {point.y for point in self.all_path_borders()}
        y_coords.update({sand.y for sand in self._sand})
        a, b = Point(min(x_coords), min(y_coords)), Point(max(x_coords), max(y_coords))

        lines = []
        for y in range(a.y, b.y + 1):
            line = ''
            for x in range(a.x, b.x + 1):
                point = Point(x, y)
                if point is self.sand_origin:
                    line += '+'
                elif point in self._rocks:
                    line += '#'
                elif point in self._sand:
                    line += 'o'
                else:
                    line += '.'
            lines.append(line)
        return '\n'.join(lines)

    @property
    def sand(self) -> int:
        return len(self._sand)

    @cached_property
    def floor(self) -> int:
        """ Any point below floor is considered fallen into void. """
        coeff = self.floor_coeff if self.floor_coeff else 0
        return self.range[1].y + coeff

    def get_fall_position(self, sand: Point) -> typing.Iterator[Point]:
        """ For given sand generate new positions that is not blocked. """
        # can go down, down-left or down-right
        for direction in DIRS:
            new_point = sand + direction
            if not self.is_blocked(new_point):
                yield new_point

    def is_blocked(self, point: Point) -> bool:
        """ Return if given point is in invalid position """
        # for part 1 there is no floor and we have void
        if self.floor_coeff is None:
            return (point in self._sand) or (point in self._rocks)
        # for part 2 the floor can block further movement too
        return (point in self._sand) or (point in self._rocks) or (point.y == self.floor)

    def in_void(self, point: Point) -> bool:
        """ Given point is falling into void. """
        return point.y >= self.floor

    def all_path_borders(self) -> typing.Iterator[Point]:
        for path in self.paths:
            yield from path.get_start_end()

    @cached_property
    def range(self) -> tuple[Point, Point]:
        x_coords = {point.x for point in self.all_path_borders()}
        y_coords = {point.y for point in self.all_path_borders()}
        return Point(min(x_coords), min(y_coords)), Point(max(x_coords), max(y_coords))

    def add_path(self, formation: str) -> None:
        points = formation.split(' -> ')
        for a, b in zip(points, points[1:]):
            new_path = Line(parse_point(a), parse_point(b))
            self.paths.append(new_path)
            new_rocks = set(new_path)
            self._rocks.update(new_rocks)

    def fall(self) -> Point | None:
        """ Simulate sand falling from origin and return where it landed. """
        curr = self.sand_origin
        while True:
            # get first non-blocked falling position
            new = next(self.get_fall_position(curr), None)
            # sand landed as there is no further falling position
            if new is None:
                return curr
            # sand fell into the void
            if self.in_void(new):
                return None
            # keep falling sand
            curr = new

    def pour_sand(self) -> None:
        """ Part 1 simulating pouring sand with void. """
        while True:
            # fall next sand
            new = self.fall()
            # we are done as all sand is pouring into void now
            if new is None:
                break
            # sand landed and can be added to the set
            self._sand.add(new)

    def pour_sand_to_floor(self) -> None:
        """ BFS to generate all positions where sand can land with floor """
        queue = deque([self.sand_origin])
        self._sand.add(self.sand_origin)
        while queue:
            current = queue.popleft()
            for neighbor in self.get_fall_position(current):
                # do not process certain position more than once
                if neighbor not in self._sand:
                    self._sand.add(neighbor)
                    queue.append(neighbor)


@timeit
def parse(input_file: Path) -> Cavern:
    cavern = Cavern(SAND_POINT)
    data = input_file.read_text().splitlines()
    for line in data:
        cavern.add_path(line)
    return cavern


# part 1
@timeit
def simulate_sand(cavern: Cavern) -> int:
    cavern.pour_sand()
    return cavern.sand


def test_simulate_sand():
    input_file = HERE / INPUT_TEST
    cavern = parse(input_file)
    count = simulate_sand(cavern)
    print(cavern)
    assert count == 24


# part 2
@timeit
def simulate_sand_with_floor(cavern: Cavern, floor_coeff: int) -> int:
    cavern.floor_coeff = floor_coeff
    cavern.pour_sand_to_floor()
    return cavern.sand


def test_simulate_sand_with_floor():
    input_file = HERE / INPUT_TEST
    cavern = parse(input_file)
    count = simulate_sand_with_floor(cavern, 2)
    print(cavern)
    assert count == 93


def main():
    input_file = HERE / INPUT_FILE
    cavern = parse(input_file)
    sand_count = simulate_sand(deepcopy(cavern))
    print(f'Amount of sand that can come down to rest before flowing into the void is: {sand_count} ')

    floor_sand_count = simulate_sand_with_floor(cavern, 2)
    print(f'Amount of sand that can come down to rest on floor is: {floor_sand_count} ')


if __name__ == "__main__":
    main()
