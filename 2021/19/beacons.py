# https://adventofcode.com/2021/day/19

from __future__ import annotations

import itertools
import logging
import os
import sys
from collections import namedtuple, defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from timeit import default_timer as timer
from typing import Iterator, NamedTuple

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

MIN_OVERLAP = 12

#  Sign and index of Rotation axis that is being rotated. Axis: x=0, y=1, z=2
Pair = namedtuple('Pair', 'sign axis')


class Rotation(NamedTuple):
    """ Rotation of any axis described by a Pair of sign and original axis. """
    x: Pair
    y: Pair
    z: Pair


class Point(NamedTuple):
    """ Point (Beacon/shift) on the grid represented by its x,y,z axis coordinates."""
    x: int
    y: int
    z: int

    def __sub__(self, other: Point) -> Point:
        """ Calculate difference (shift) of two points.  """
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other) -> Point:
        """ Calculate sum of two Points (shifting of original). """
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def manhattan_distance(self, other: Point) -> int:
        """ Calculate Manhattan Distance to another point. """
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)

    def rotate(self, rotation: Rotation) -> Point:
        """ Rotate the point in any axis. """
        if rotation == Rotation(Pair(1, 0), Pair(1, 1), Pair(1, 2)):
            # identity, no rotation needed
            return self
        return Point(*tuple(pair.sign * self[pair.axis] for pair in rotation))


@dataclass
class Grid:
    """
        Grid represents continuous area scanned by Scanner from Point(0,0,0) storing all beacons it found.
        Each grid can be fixed (matched to another grid) by rotation and shift.
        Grid overlap can be efficiently found by comparing set of all distances between all pairs of beacons.
    """
    beacons: set[Point]
    fixed: bool = False
    idx: int = field(default_factory=itertools.count().__next__, init=False)
    distances: dict[tuple[Point, Point], int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """ Calculate manhattan distances between all points stored on grid. """
        for beacon, other in combinations(self.beacons, 2):
            self.distances[beacon, other] = beacon.manhattan_distance(other)

    def rotate(self, rotation: Rotation) -> Grid:
        """ Return copy of Grid rotated by given rotation. """
        if rotation == Rotation(Pair(1, 0), Pair(1, 1), Pair(1, 2)):
            return self
        rotated_beacons = {beacon.rotate(rotation) for beacon in self.beacons}
        return Grid(rotated_beacons)

    def shift(self, shift: Point) -> Grid:
        """ Return copy of Grid shifted by given shift. """
        if shift == Point(0, 0, 0):
            return self
        shifted = {beacon + shift for beacon in self.beacons}
        return Grid(shifted)

    def overlaps(self, other: Grid) -> bool:
        """ If grid overlaps with another in at least 12 beacons. """
        overlap = set(self.distances.values()) & set(other.distances.values())
        return len(overlap) >= len(list(combinations(range(MIN_OVERLAP), 2)))

    def match_grid(self, other: Grid) -> Point:
        """ Rotate and shift given grid based on its overlap so both are fixed in same starting position. """
        assert self.fixed is True
        if other.fixed:
            return Point(0, 0, 0)
        # try all pairs of beacons to find identity after rotation
        for beacon in self.beacons:
            for other_beacon in other.beacons:
                for rotation in generate_rotations():
                    shift = beacon - other_beacon.rotate(rotation)
                    candidate = other.rotate(rotation).shift(shift)
                    overlap = self.beacons & candidate.beacons
                    if len(overlap) >= MIN_OVERLAP:
                        other.beacons = candidate.beacons
                        other.fixed = True
                        logging.debug(f'Scanner {self.idx} matched to {other.idx} at {shift}.')
                        return shift
        raise ValueError('No overlap found, but there should be!')


def generate_rotations() -> Iterator[Rotation]:
    """ Generate all rotations in 90 degree turns along any axis. """
    rotation_definitions = [
        '+x+y+z', '-x+y-z', '+y-x+z', '-y-x-z', '+z+x+y', '-z+x-y',
        '+x-z+y', '-x+z+y', '+y-z-x', '-y+z-x', '+z-y+x', '-z+y+x',
        '+x-y-z', '-x-y+z', '+y+x-z', '-y+x+z', '+z-x-y', '-z-x+y',
        '+x+z-y', '-x-z-y', '+y+z+x', '-y-z+x', '+z+y-x', '-z-y-x',
    ]
    translate = {'+': 1, '-': -1, 'x': 0, 'y': 1, 'z': 2}
    for definition in rotation_definitions:
        pairs = [Pair(translate[definition[idx]], translate[definition[idx + 1]]) for idx in (0, 2, 4)]
        yield Rotation(*pairs)


def parse_file(input_file: str) -> list[Grid]:
    """ Parse given file into list of scanned Grids. """
    grids = []
    with open(input_file) as f:
        beacons = set()
        for line in f:
            line = line.strip()
            if not line:
                grids.append(Grid(beacons))
                beacons = set()
            elif 'scanner' in line:
                continue
            else:
                x, y, z = line.split(',')
                beacons.add(Point(int(x), int(y), int(z)))
        grids.append(Grid(beacons))

    return grids


# part 1 & 2
def calculate_beacons(scanners: list[Grid]) -> tuple[int, list[Point]]:
    """ Match/fix all scanned grids to the same grid to find total count of beacons. """
    scanner: Grid
    other_scanner: Grid
    overlaps = defaultdict(list)
    for scanner, other_scanner in combinations(scanners, 2):
        if scanner.overlaps(other_scanner):
            overlaps[scanner.idx].append(other_scanner.idx)
            overlaps[other_scanner.idx].append(scanner.idx)

    found_shifts = []
    start_idx = 0
    queue = [start_idx]
    scanners[start_idx].fixed = True
    while queue:
        # grid from queue that is already fixed
        idx = queue.pop(start_idx)
        # for all the other grids that overlap with it
        for other_idx in overlaps[idx]:
            # skip the grid that is already fixed
            if scanners[other_idx].fixed:
                continue
            # find shift needed to match the grid
            found_shifts.append(scanners[idx].match_grid(scanners[other_idx]))
            # add the grid to the queue to fix its overlapping grids too
            if other_idx not in queue:
                queue.append(other_idx)
    # merge all found beacons in fixed grids to find their sum
    all_beacons = set()
    for scanner in scanners:
        all_beacons |= scanner.beacons

    return len(all_beacons), found_shifts


def test_calculate_beacons():
    scanners = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_count, test_shifts = calculate_beacons(scanners)
    test_distance = max(
        scanner.manhattan_distance(other_scanner) for scanner, other_scanner in combinations(test_shifts, 2)
    )
    assert test_count == 79
    assert test_distance == 3621


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    final_count, final_shifts = calculate_beacons(parse_file(INPUT_FILE))
    max_distance = max(
        scanner.manhattan_distance(other_scanner) for scanner, other_scanner in combinations(final_shifts, 2)
    )
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final beacon count is {final_count} and maximum distance between scanners is {max_distance}.')
