# https://adventofcode.com/2023/day/3

from typing import Iterator
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from libs import timeit, Point, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()
DIRS = {Point(0, -1), Point(1, -1), Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0), Point(-1, -1)}


@dataclass(eq=True, frozen=True)
class Number:
    _value: str
    origin: Point

    def __int__(self) -> int:
        return int(self._value)

    def __iter__(self) -> Iterator[Point]:
        for i in range(len(self._value)):
            yield self.origin + Point(i, 0)

    def get_neighbors(self) -> set[Point]:
        neighbors = set()
        for point in self:
            for direction in DIRS:
                neighbor = point + direction
                if neighbor not in self:
                    neighbors.add(neighbor)
        return neighbors


@dataclass
class Grid:
    numbers: set[Number]
    parts: dict[Point, str]
    parts_numbers: dict[Point, set[Number]] = field(init=False)

    def __post_init__(self):
        self.parts_numbers = defaultdict(set)
        self.generate_parts_numbers()

    def generate_parts_numbers(self) -> None:
        """For each part find and store all numbers that are adjacent."""
        parts = set(self.parts.keys())
        for number in self.numbers:
            intersection = parts.intersection(number.get_neighbors())
            for part_point in intersection:
                self.parts_numbers[part_point].add(number)

    def get_numbers_around_parts(self) -> set[Number]:
        """Get all part numbers that are adjacent to at least one part."""
        all_numbers = set()
        for numbers in self.parts_numbers.values():
            all_numbers.update(numbers)
        return all_numbers

    def generate_gear_power(self) -> Iterator[int]:
        """
        Gear is defined as '*' part with exactly two numbers around.
        For each gear compute it's power by multiplying the value of adjacent numbers.
        """
        for point, value in self.parts.items():
            if value == "*" and len(self.parts_numbers[point]) == 2:
                a, b = self.parts_numbers[point]
                yield int(a) * int(b)


def parse_file(input_file: Path) -> Grid:
    numbers = set()
    parts = dict()
    y = 0
    for line in input_file.read_text().splitlines():
        line = line.strip()
        x = 0
        curr_number = ""
        origin = None
        for char in line:
            if char.isdigit():
                if not curr_number:
                    origin = Point(x, y)
                curr_number += char
            elif curr_number and origin is not None:
                numbers.add(Number(_value=curr_number, origin=origin))
                curr_number = ""
                origin = None
            if not char.isdigit() and char != ".":
                parts[Point(x, y)] = char
            x += 1
        else:
            if curr_number and origin is not None:
                numbers.add(Number(_value=curr_number, origin=origin))
        y += 1
    return Grid(numbers, parts)


# part 1
@timeit
def find_part_numbers(grid: Grid) -> list[Number]:
    part_numbers = [int(num) for num in grid.get_numbers_around_parts()]
    return part_numbers


def test_find_part_numbers():
    grid = parse_file(HERE / INPUT_TEST)
    test_part_numbers = find_part_numbers(grid)
    assert sum(test_part_numbers) == 4361


# part 2
@timeit
def find_gears_power(grid: Grid) -> list[int]:
    gears_powers = list(grid.generate_gear_power())
    return gears_powers


def test_find_gears_power():
    grid = parse_file(HERE / INPUT_TEST)
    test_powers = find_gears_power(grid)
    assert sum(test_powers) == 467835


if __name__ == "__main__":
    grid = parse_file(HERE / INPUT_FILE)

    final_numbers = find_part_numbers(grid)
    print(f"Sum of all part numbers: {sum(final_numbers)}")

    final_powers = find_gears_power(grid)
    print(f"Sum of all gears powers: {sum(final_powers)}")
