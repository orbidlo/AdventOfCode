# https://adventofcode.com/2021/day/22

from __future__ import annotations

import logging
import os
import re
import sys
from dataclasses import dataclass, field
from itertools import product
from timeit import default_timer as timer
from typing import Iterator, NamedTuple, Any

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'
INPUT_TEST2 = 'input_test2.txt'
REGEX = r'x=(?P<x1>[-\d]+)\.\.(?P<x2>[-\d]+),y=(?P<y1>[-\d]+)\.\.(?P<y2>[-\d]+),z=(?P<z1>[-\d]+)\.\.(?P<z2>[-\d]+)'


class Voxel(NamedTuple):
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class Range:
    """
        Class implementing distance from min to max (both included).
        Has ability to detect overlapping with another and to split by intersection.
    """
    min: int
    max: int

    def __post_init__(self):
        assert self.min <= self.max, 'First parameter of range must be lower or equal to the second one.'

    def __len__(self):
        """ Length of range. """
        return self.max - self.min + 1

    def __eq__(self, other: Range) -> bool:
        return self.min == other.min and self.max == other.max

    def __iter__(self) -> Iterator[Range]:
        yield self.min
        yield self.max

    def __contains__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.min <= other <= self.max
        if isinstance(other, Range):
            if self == other:
                return True
            return other.min in self and other.max in self
        raise NotImplementedError

    def overlaps(self, other: Range) -> bool:
        return self.max >= other.min and self.min <= other.max

    def get_intersection(self, other: Range) -> Range | None:
        if self == other:
            return self
        new_range_min, new_range_max = max(self.min, other.min), min(self.max, other.max)
        if new_range_min > new_range_max:
            # no intersection
            return None
        return Range(new_range_min, new_range_max)

    def split(self, item: Any) -> list[Range]:
        """ Split range by intersection with another range. """
        if isinstance(item, Range):
            if self == item:
                return [self]
            intersection = self.get_intersection(item)
            assert intersection is not None, "Cannot split range if it doesn't have intersection with the other."
            if self.min == intersection.min:
                return [intersection, Range(intersection.max + 1, self.max)]
            if self.max == intersection.max:
                return [Range(self.min, intersection.min - 1), intersection]
            # intersection is within self
            return [Range(self.min, intersection.min - 1), intersection, Range(intersection.max + 1, self.max)]
        raise NotImplementedError


class Cuboid(NamedTuple):
    x: Range
    y: Range
    z: Range

    def __len__(self):
        """ Volume of cuboid. """
        return len(self.x) * len(self.y) * len(self.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, (Cuboid, Voxel)):
            return item.x in self.x and item.y in self.y and item.z in self.z
        raise NotImplementedError

    def overlaps(self, other: Cuboid) -> bool:
        if self == other:
            return True
        return all(axis.overlaps(other_axis) for axis, other_axis in zip(self, other))

    def get_intersection(self, other: Cuboid) -> Cuboid | None:
        if self == other:
            return self
        ranges = []
        for axis, other_axis in zip(self, other):
            axis_intersection = axis.get_intersection(other_axis)
            if axis_intersection is None:
                return None
            ranges.append(axis_intersection)
        return Cuboid(*ranges)

    def extract(self, other: Cuboid) -> set[Cuboid]:
        """ Split self, extract intersection with another cuboid and return rest of sub-cuboids. """
        new_cuboids = set()
        if self == other:
            return set()
        intersection = self.get_intersection(other)
        assert intersection is not None, "Cannot split cuboid if it doesn't have intersection with the other."
        split_ranges = []
        for axis, other_axis in zip(self, intersection):
            split_ranges.append(axis.split(other_axis))
        for x, y, z in product(*split_ranges):
            new_cuboid = Cuboid(x, y, z)
            if new_cuboid != intersection:
                new_cuboids.add(new_cuboid)
        logging.debug(f'Splitting into {len(new_cuboids)} new cuboids.'
                      f'\nThrowing away {intersection}.')
        return new_cuboids


@dataclass
class EfficientGrid:
    """ Efficient grid with ability to store all non-overlapping lit cuboids within by their range definition. """
    _lit_cuboids: set[Cuboid] = field(default_factory=set, init=False)

    def add_lit(self, cuboid: Cuboid) -> None:
        """ Add lit cuboid. If it overlaps with one already stored, split it, extract intersection and add the rest. """
        queue = [cuboid]
        lit_to_remove = set()
        lit_to_add = set()
        while queue:
            new_cuboid = queue.pop()
            for lit_cuboid in self._lit_cuboids:
                if new_cuboid in lit_cuboid:
                    # cuboid is already lit, move to another in queue
                    break
                if lit_cuboid in new_cuboid:
                    # new cuboid is around lit cuboid, so replace it and search the rest
                    lit_to_remove.add(lit_cuboid)
                elif new_cuboid.overlaps(lit_cuboid):
                    # new cuboid overlaps with some lit cuboid, so split it, extract intersections and add the rest
                    new_cuboids = new_cuboid.extract(lit_cuboid)
                    queue.extend(new_cuboids)
                    break
            else:
                # run this if we didn't break from for cycle or skipped it due to no members
                lit_to_add.add(new_cuboid)
            self._lit_cuboids = self._lit_cuboids - lit_to_remove
            self._lit_cuboids |= lit_to_add

    def remove_lit(self, cuboid: Cuboid) -> None:
        """ Remove cuboid from lit cuboids. If it overlaps with existing one, split it to remove intersection. """
        lit_to_remove = set()
        lit_to_add = set()
        for lit_cuboid in self._lit_cuboids:
            if lit_cuboid in cuboid:
                # remove lit cuboids if they are same or smaller size
                lit_to_remove.add(lit_cuboid)
            elif cuboid.overlaps(lit_cuboid):
                # new cuboid overlaps with lit cuboid, so split the lit one and remove intersection
                new_lit_cuboids = lit_cuboid.extract(cuboid)
                lit_to_remove.add(lit_cuboid)
                lit_to_add |= new_lit_cuboids
        self._lit_cuboids = self._lit_cuboids - lit_to_remove
        self._lit_cuboids |= lit_to_add

    @classmethod
    def parse_instructions(cls, instructions: list[tuple[bool, Cuboid]]) -> EfficientGrid:
        """ Parse instructions to create efficient grid with non-overlapping lit cuboids. """
        grid = cls()
        for sign, new_cuboid in instructions:
            if sign:
                grid.add_lit(new_cuboid)
            else:
                grid.remove_lit(new_cuboid)
        return grid

    def count_lit(self) -> int:
        """ Total count of lit voxels on the grid. """
        return sum(len(cuboid) for cuboid in self._lit_cuboids)


@dataclass()
class Grid:
    """
        Grid with sparse matrix of all lit cubes centered around voxels parsed from lit cuboids.
    """
    _lit_cubes: set[Voxel] = field(default_factory=set, init=False)

    @classmethod
    def parse_instructions(cls, instructions: list[tuple[bool, Cuboid]]) -> Grid:
        """ Parse instructions to create simple grid storing all lit cubes.  """
        grid = cls()
        for sign, cuboid in instructions:
            if cuboid:
                grid.switch_light(sign, cuboid)
        return grid

    def count_lit(self) -> int:
        """ Total count of lit pixels on the grid. """
        return len(self._lit_cubes)

    def is_lit(self, voxel: Voxel) -> bool:
        """ If given voxel is lit. """
        return voxel in self._lit_cubes

    def switch_light(self, turn_on: bool, cuboid: Cuboid) -> None:
        for x in range(cuboid.x.min, cuboid.x.max + 1):
            for y in range(cuboid.y.min, cuboid.y.max + 1):
                for z in range(cuboid.z.min, cuboid.z.max + 1):
                    voxel = Voxel(x, y, z)
                    if turn_on:
                        self._lit_cubes.add(voxel)
                    else:
                        self._lit_cubes.discard(voxel)


def cut_off(cuboid: Cuboid, limit=Range(-50, 50)) -> Cuboid | None:
    """ Cut off cuboid to fit within given range on all axis. """
    ranges = []
    for axis in cuboid:
        a, b = axis
        new_a = a
        new_b = b
        if a < limit.min:
            new_a = limit.min
        if a > limit.max:
            logging.debug(f'\nThrowing off {cuboid} due to invalid range {a, b}!')
            return None
        if b < limit.min:
            logging.debug(f'\nThrowing off {cuboid} due to invalid range {a, b}!')
            return None
        if b > limit.max:
            new_b = limit.max
        if a != new_a or b != new_b:
            logging.debug(f'Cutting off range {a, b} to {new_a, new_b}!')
        ranges.append(Range(new_a, new_b))
    return Cuboid(*ranges)


def parse_file(input_file: str, cutoff: bool) -> list[tuple[bool, Cuboid]]:
    """ Parse given file into Cuboids with signal on or off and optionally cut off by given limit."""
    lines = []

    with open(input_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            signal, rest = line.split()
            signal = (signal == 'on')
            match = re.search(REGEX, rest)
            x_range = Range(int(match.group('x1')), int(match.group('x2')))
            y_range = Range(int(match.group('y1')), int(match.group('y2')))
            z_range = Range(int(match.group('z1')), int(match.group('z2')))
            cuboid = Cuboid(x_range, y_range, z_range)
            if cutoff:
                cuboid = cut_off(cuboid)
            lines.append((signal, cuboid))
    return lines


# part 1
def count_lit_cubes_with_cutoff(instructions: list[tuple[bool, Cuboid]]) -> int:
    grid = Grid.parse_instructions(instructions)
    return grid.count_lit()


def test_count_lit_cubes_with_cutoff():
    instructions = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST), cutoff=True)
    test_count = count_lit_cubes_with_cutoff(instructions)
    assert test_count == 590784


# part 2
def count_lit_cubes(instructions: list[tuple[bool, Cuboid]]) -> int:
    grid = EfficientGrid.parse_instructions(instructions)
    return grid.count_lit()


def test_count_lit_cubes():
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    instructions = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST2), cutoff=False)
    test_count = count_lit_cubes(instructions)
    assert test_count == 2758514936282235


def test_cuboid_overlap():
    cuboid_1 = Cuboid(Range(1, 2), Range(1, 2), Range(1, 2))
    cuboid_2 = Cuboid(Range(2, 3), Range(-1, 1), Range(-1, 3))
    cuboid_3 = Cuboid(Range(5, 6), Range(-6, -5), Range(0, 0))
    assert cuboid_1.overlaps(cuboid_1)
    assert cuboid_1.overlaps(cuboid_2)
    assert cuboid_2.overlaps(cuboid_1)
    assert not cuboid_1.overlaps(cuboid_3)


def test_cuboid_split():
    cuboid_1 = Cuboid(Range(1, 3), Range(1, 3), Range(1, 3))
    cuboid_2 = Cuboid(Range(2, 2), Range(2, 2), Range(1, 3))
    cuboid_3 = Cuboid(Range(2, 2), Range(2, 2), Range(2, 2))
    new_cuboids = cuboid_1.extract(cuboid_2)
    assert len(new_cuboids) == 8
    assert cuboid_1.get_intersection(cuboid_2) not in new_cuboids
    new_cuboids = cuboid_1.extract(cuboid_3)
    assert len(new_cuboids) == 26
    assert cuboid_1.get_intersection(cuboid_3) not in new_cuboids


def test_range_get_intersection():
    range_1 = Range(0, 5)
    range_2 = Range(-3, 3)
    range_3 = Range(6, 8)
    assert range_1.get_intersection(range_2) == Range(0, 3)
    assert range_1.get_intersection(range_3) is None


def test_cuboid_contains():
    cuboid_1 = Cuboid(Range(1, 2), Range(1, 2), Range(1, 2))
    cuboid_2 = Cuboid(Range(0, 3), Range(-1, 2), Range(1, 2))
    assert cuboid_1 in cuboid_1
    assert cuboid_1 in cuboid_2
    assert cuboid_2 not in cuboid_1


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    final_instructions = parse_file(INPUT_FILE, cutoff=True)
    final_counter = count_lit_cubes_with_cutoff(final_instructions)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final count of lit cubes (cut off to -50, 50) within grid is {final_counter}.')

    start_time = timer()
    final_instructions = parse_file(INPUT_FILE, cutoff=False)
    final_counter = count_lit_cubes(final_instructions)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final count of lit cubes within grid is {final_counter}.')
