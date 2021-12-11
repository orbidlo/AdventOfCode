# https://adventofcode.com/2021/day/11

from timeit import default_timer as timer
from dataclasses import dataclass
from collections import namedtuple

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

STEPS = 100
FLASH_POINT = 9

Point = namedtuple('Point', 'x y')


@dataclass(frozen=False)
class Cavern:
    """ Represent cavern full of octopuses and their flashing in darkness. """
    _levels: list[list[int]]  # Levels of brightness of each octopus
    flashes: int = 0

    def __post_init__(self):
        if not self._levels:
            raise ValueError('Must provide non-empty list of lists when creating cavern.')

    @property
    def shape(self) -> tuple[int, int]:
        """ Shape of cave X x Y """
        return len(self._levels[0]), len(self._levels)

    @property
    def count(self):
        """ Total count of octopuses in cavern """
        return len(self._levels[0]) * len(self._levels)

    def __getitem__(self, point: Point) -> int:
        return self._levels[point.y][point.x]

    def __setitem__(self, key: Point, value: int) -> None:
        self._levels[key.y][key.x] = value

    def __repr__(self) -> str:
        return '\n' + '\n'.join(str(row) for row in self._levels)

    def is_within_boundary(self, point: Point) -> bool:
        """ If given point exists within Cavern boundary """
        width, height = self.shape
        return (0 <= point.x < width) and (0 <= point.y < height)

    def get_adjacent(self, point: Point) -> Point:
        """ For given point generates adjacent points (including diagonal) within Cavern boundary. """
        coords = {(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)}

        for adj in [Point(point.x + x, point.y + y) for x, y in coords]:
            if self.is_within_boundary(adj):
                yield adj

    def raise_level(self, point: Point, flashed: set) -> None:
        """ Raises level of given point and flash neighbors if conditions are met. """
        if point in flashed:
            # skip if already flashed this step
            pass
        elif self[point] == FLASH_POINT:
            # reset if we reached flash point and raise all neighbors by 1
            self[point] = 0
            flashed.add(point)
            self.flashes += 1
            for adj in self.get_adjacent(point):
                self.raise_level(adj, flashed)
        else:
            self[point] += 1

    def step(self, flashed_this_step):
        """ Run one day in cavern that raises level by 1 """
        for width in range(self.shape[0]):
            for height in range(self.shape[1]):
                point = Point(width, height)
                self.raise_level(point, flashed=flashed_this_step)


def parse_lines(input_file) -> list[list[int]]:
    lines = []
    with open(input_file) as f:
        for line in f:
            lines.append([int(x) for x in list(line.strip())])
    return lines


def count_flashes(input_file: str) -> int:
    cavern = Cavern(parse_lines(input_file))
    for day in range(STEPS):
        flashed_this_step = set()
        cavern.step(flashed_this_step)
        logging.debug(f'Day {day + 1}: flashed {len(flashed_this_step)} times!\n')
        logging.debug(cavern)
    return cavern.flashes


def test_count_flashes():
    test_count = count_flashes(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 1656


# part 2
def get_step_all_flash(input_file: str) -> int:
    cavern = Cavern(parse_lines(input_file))
    day = 0
    while True:
        flashed_this_step = set()
        day += 1
        cavern.step(flashed_this_step)
        count = len(flashed_this_step)
        logging.debug(f'Day {day}: flashed {count} times!\n')
        if count == cavern.count:
            logging.debug(f'Day {day} all flashed!')
            return day


def test_get_step_all_flash():
    test_step = get_step_all_flash(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_step == 195


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    total_count = count_flashes(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Number of flashes after {STEPS} days is {total_count}.')

    start = timer()
    step = get_step_all_flash(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) On {step}\'th day all octopuses flashed!')
