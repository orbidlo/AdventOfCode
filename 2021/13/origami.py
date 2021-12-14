# https://adventofcode.com/2021/day/13

from __future__ import annotations

from timeit import default_timer as timer
from dataclasses import dataclass, field
from collections import namedtuple

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Point = namedtuple('Point', ['x', 'y'])


@dataclass
class Origami:
    """ Represents origami paper with points on it and how it is affected by folding. """
    max_folds: int
    _num_folds = 0
    _fold_width: int = 0
    _fold_height: int = 0
    _paper: set[Point] = field(default_factory=set, init=False)

    @classmethod
    def parse_file(cls, input_file, max_folds: int) -> Origami:
        origami = cls(max_folds)
        with open(input_file) as f:
            for line in f:
                if 'fold along y=' in line:
                    _, num = line.strip().split('=')
                    origami.add_fold(line_y=int(num))
                elif 'fold along x=' in line:
                    _, num = line.strip().split('=')
                    origami.add_fold(line_x=int(num))
                elif line.strip():
                    x, y = line.strip().split(',')
                    origami.add_point(int(x), int(y))
        return origami

    def __len__(self) -> int:
        return len(self._paper)

    def __repr__(self) -> str:
        rows = []
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                point = Point(x, y)
                row += '#' if point in self._paper else '.'
            rows.append(row)
        return '\n' + '\n'.join(row for row in rows)

    @property
    def width(self) -> int:
        return self._fold_width

    @property
    def height(self) -> int:
        return self._fold_height

    def add_point(self, x: int, y: int) -> None:
        """ Adds point on origami paper. """
        self._paper.add(Point(x, y))

    def add_fold(self, line_x: int = None, line_y: int = None) -> None:
        """ Folds origami paper up or left. """
        if self.max_folds and self._num_folds >= self.max_folds:
            # skip fold if we reached maximum of folds
            return
        if line_x:
            # we are folding to the left
            self._fold_width = line_x
            for point in self._paper.copy():
                if point.x > self._fold_width:
                    # this point is to the right from fold and needs to be flipped
                    self._paper.remove(point)
                    flipped_point = Point(2 * line_x - point.x, point.y)
                    if flipped_point.x >= 0:
                        self._paper.add(flipped_point)
                    else:  # point is flipped beyond border of paper
                        logging.debug(f'Discarding {point} (flipped to {flipped_point}')
        elif line_y:
            # we are folding up
            self._fold_height = line_y
            for point in self._paper.copy():
                if point.y > self._fold_height:
                    # this point is down from fold and needs to be flipped
                    self._paper.remove(point)
                    flipped_point = Point(point.x, 2 * line_y - point.y)
                    if flipped_point.y >= 0:
                        self._paper.add(flipped_point)
                    else:  # point is flipped beyond border of paper
                        logging.debug(f'Discarding {flipped_point}')
        self._num_folds += 1


# part 1+2
def count_points(input_file: str, max_folds: int) -> int:
    origami = Origami.parse_file(input_file, max_folds)
    logging.info(origami)
    return len(origami)


def test_count_points_after_1_fold():
    test_count = count_points(os.path.join(os.path.dirname(__file__), INPUT_TEST), max_folds=1)
    assert test_count == 17


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    total_count = count_points(INPUT_FILE, max_folds=0)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Total visible dots after first fold is {total_count}.')

