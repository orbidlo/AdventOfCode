# https://adventofcode.com/2021/day/20

from __future__ import annotations

import logging
import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from timeit import default_timer as timer

import pytest

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Pixel = namedtuple('Point', 'x y')


def parse_file(input_file: str) -> Grid:
    """ Parse given file into Grid. """
    with open(input_file) as f:
        algorithm = [1 if char == '#' else 0 for char in list(f.readline().strip())]
        pixels = set()
        y = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            for x, char in enumerate(line):
                if char == '#':
                    pixels.add(Pixel(x, y))
            y += 1

    return Grid(pixels, algorithm)


@dataclass()
class Grid:
    """
        Grid with sparse matrix of lit pixels, infinity representation and
        ability to enhance image based on given algorithm.
    """
    _lit_pixels: set[Pixel]
    enhance_algorithm: list[int]
    infinity: int = 0
    width: tuple[int, int] = field(init=False)
    height: tuple[int, int] = field(init=False)

    def __post_init__(self):
        self.width = min(pixel.x for pixel in self._lit_pixels), max(pixel.x for pixel in self._lit_pixels)
        self.height = min(pixel.y for pixel in self._lit_pixels), max(pixel.y for pixel in self._lit_pixels)

    def count_lit(self):
        """ Total count of lit pixels on the grid. """
        return len(self._lit_pixels)

    def in_grid(self, pixel: Pixel) -> bool:
        """ If given pixel is within grid defined by its lit pixels. """
        min_x, max_x = self.width
        min_y, max_y = self.height
        return min_x <= pixel.x <= max_x and min_y <= pixel.y <= max_y

    def is_lit(self, pixel: Pixel) -> bool:
        """ If given pixel is lit. """
        if not self.in_grid(pixel):
            return bool(self.infinity)
        return pixel in self._lit_pixels

    def __repr__(self) -> str:
        result = ''
        min_x, max_x = self.width
        min_y, max_y = self.height
        for y in range(min_y - 3, max_y + 4):
            result += '\n' + ''.join('#' if self.is_lit(Pixel(x, y)) else '.' for x in range(min_x - 3, max_x + 4))
        return result

    @staticmethod
    def generate_input_matrix(pixel: Pixel) -> Pixel:
        """ For given pixel generate all pixels in 3x3 matrix around it. """
        matrix = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        for adj in [Pixel(pixel.x + x, pixel.y + y) for x, y in matrix]:
            yield adj

    def is_output_lit(self, pixel: Pixel) -> bool:
        """ For given output pixel compute if the pixel is lit using enhancement algorithm.  """
        # Check input matrix for 9-bit binary number (read row by row)
        binary_str = ''.join('1' if self.is_lit(adj) else '0' for adj in self.generate_input_matrix(pixel))
        # binary number converted to integer is index within enhancement algorithm saying if output is lit or not
        idx = int(binary_str, 2)
        return bool(self.enhance_algorithm[idx])

    def enhance(self) -> Grid:
        """ Create output grid based on enhancement algorithm. """
        enhanced = set()
        min_x, max_x = self.width
        min_y, max_y = self.height
        # generate pixels in the grid and on the edge of it
        for y in range(min_y - 1, max_y + 2):
            for x in range(min_x - 1, max_x + 2):
                output_pixel = Pixel(x, y)
                # check output pixel and add it to new grid, if lit
                if self.is_output_lit(output_pixel):
                    enhanced.add(output_pixel)
        # generate pixels beyond edge to infinity
        new_infinity = self.infinity
        if self.infinity and not self.enhance_algorithm[-1]:
            # infinity is unlit if lit
            new_infinity = 0
        elif not self.infinity and self.enhance_algorithm[0]:
            # infinity is lit if unlit
            new_infinity = 1
        grid = Grid(enhanced, self.enhance_algorithm)
        grid.infinity = new_infinity
        return grid


# part 1
def count_lit_pixels(grid: Grid, steps: int) -> int:
    """ Count lit pixels within grid after enhancing it `steps` times. """
    for _ in range(0, steps):
        grid = grid.enhance()
    return grid.count_lit()


@pytest.mark.parametrize(
    "steps,expected", [
        (2, 35),
        (50, 3351)
    ])
def test_count_lit_pixels(steps, expected):
    grid = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_count = count_lit_pixels(grid, steps=steps)
    assert test_count == expected


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    part_1_count = count_lit_pixels(parse_file(INPUT_FILE), steps=2)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final count of lit pixels after 2 enhancements is {part_1_count}.')

    start_time = timer()
    part_2_count = count_lit_pixels(parse_file(INPUT_FILE), steps=50)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final count of lit pixels after 50 enhancements is {part_2_count}.')
