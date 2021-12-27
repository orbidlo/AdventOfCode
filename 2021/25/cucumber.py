# https://adventofcode.com/2021/day/25

from __future__ import annotations

import logging
import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
from timeit import default_timer as timer

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Point = namedtuple('Point', 'x y')


class Direction(Enum):
    SOUTH = 'v'
    EAST = '>'
    NONE = '.'


OFFSET = {
    Direction.SOUTH: Point(0, 1),
    Direction.EAST: Point(1, 0)
}


@dataclass
class Grid:
    """ Grid of cucumbers that are able to move together, east then south herd. """
    width: int
    height: int
    cucumbers: dict[Point, Direction] = field(default_factory=dict)

    def __repr__(self) -> str:
        rows = []
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                point = Point(x, y)
                row += self.cucumbers.get(point, Direction.NONE).value
            rows.append(row)
        return '\n' + '\n'.join(row for row in rows)

    @classmethod
    def parse_file(cls, input_file: str) -> Grid:
        """ Parse file into Grid of cucumbers of set width and height. """
        cucumbers = dict()
        with open(input_file) as f:
            y = 0
            x = 0
            for line in f:
                line = line.strip()
                for x, char in enumerate(line):
                    if char != '.':
                        cucumbers[Point(x, y)] = Direction(char)
                y += 1
        grid = cls(x + 1, y, cucumbers)
        return grid

    def wrap(self, key: Point) -> Point:
        """ Wrap point around to stay within grid. """
        x = key.x % self.width
        y = key.y % self.height
        return Point(x, y)

    def move_herd(self, direction: Direction) -> int:
        """ Move all cucumbers with given direction if there is an empty space for them to go. """
        moved_points = dict()
        moved_count = 0
        offset = OFFSET[direction]
        for point in self.cucumbers:
            if self.cucumbers[point] == direction:
                new_point = self.wrap(Point(point.x + offset.x, point.y + offset.y))
                if new_point not in self.cucumbers:
                    # can move to empty position
                    moved_points[new_point] = self.cucumbers[point]
                    moved_count += 1
                    continue
            moved_points[point] = self.cucumbers[point]
        self.cucumbers = moved_points
        return moved_count

    def move(self) -> int:
        """ Move all cucumbers, east then south herd and return how many moved. """
        moved_count = 0
        moved_count += self.move_herd(Direction.EAST)
        moved_count += self.move_herd(Direction.SOUTH)
        return moved_count


# part 1
def move_until_total_stop(grid: Grid) -> int:
    """ Move all cucumbers until they stop moving. """
    step = 1
    while grid.move():
        step += 1
    return step


def test_move_until_total_stop():
    grid = Grid.parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_step = move_until_total_stop(grid)
    assert test_step == 58


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    final_counter = move_until_total_stop(Grid.parse_file(INPUT_FILE))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final step when all cucumbers stop moving is {final_counter}.')
