# https://adventofcode.com/2022/day/4

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Any

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()


@dataclass(frozen=True)
class Range:
    """
        Class implementing distance from min to max (both included).
        Has ability to detect overlapping with another.
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


def parse(line: str) -> tuple[Range, Range]:
    range_1, range_2 = line.split(',')
    range_1_min, range_1_max = range_1.split('-')
    range_2_min, range_2_max = range_2.split('-')
    return Range(int(range_1_min), int(range_1_max)), Range(int(range_2_min), int(range_2_max))


# part 1
def count_full_overlap(input_file: Path) -> int:
    data = input_file.read_text().splitlines()
    counter = 0
    for line in data:
        range_1, range_2 = parse(line)
        if (range_1 in range_2) or (range_2 in range_1):
            counter += 1
    return counter


def test_count_full_overlap():
    test_overlap_count = count_full_overlap(HERE / INPUT_TEST)
    assert test_overlap_count == 2


# part 2
def count_any_overlap(input_file: Path) -> int:
    data = input_file.read_text().splitlines()
    counter = 0
    for line in data:
        range_1, range_2 = parse(line)
        if range_1.overlaps(range_2):
            counter += 1
    return counter


def test_count_any_overlap():
    test_overlap_count = count_any_overlap(HERE / INPUT_TEST)
    assert test_overlap_count == 4


if __name__ == "__main__":
    full_overlap_count = count_full_overlap(HERE / INPUT_FILE)
    print(f'The number of fully overlapped sections within given pairs is {full_overlap_count}.')
    overlap_count = count_any_overlap(HERE / INPUT_FILE)
    print(f'The number of overlapped sections within given pairs is {overlap_count}.')
