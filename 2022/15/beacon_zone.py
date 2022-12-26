# https://adventofcode.com/2022/day/15

from __future__ import annotations

import re
import typing
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, Point, Range

HERE = Path(__file__).parent.resolve()
TEST_LINE = 10
INPUT_LINE = 2000000
TEST_BEACON_RANGE = Range(0, 20)
BEACON_RANGE = Range(0, 4000000)
FREQ_MULTIPLIER = 4000000


class Dirs(Enum):
    UR = Point(1, -1)
    DR = Point(1, 1)
    DL = Point(-1, 1)
    UL = Point(-1, -1)


@dataclass
class Grid:
    sensors: list[Point]
    beacons: list[Point]
    sensor_radius: dict[Point, int]

    @cached_property
    def width(self) -> tuple[int, int]:
        x_coords = [sensor.x for sensor in self.sensors]
        x_coords += [beacon.x for beacon in self.beacons]
        return min(x_coords), max(x_coords) + 1

    @cached_property
    def height(self) -> tuple[int, int]:
        y_coords = [sensor.y for sensor in self.sensors]
        y_coords += [beacon.y for beacon in self.beacons]
        return min(y_coords), max(y_coords) + 1

    def __repr__(self) -> str:
        lines = []
        for y in range(*self.height):
            line = ''
            for x in range(*self.width):
                point = Point(x, y)
                if point in self.beacons:
                    char = 'B'
                elif point in self.sensors:
                    char = 'S'
                else:
                    char = '.'
                line += char
            lines.append(line)
        return '\n'.join(lines)

    def get_sensor_coverage_at_line(self, sensor: Point, y: int) -> Range | None:
        sensor_radius = self.sensor_radius[sensor]
        distance = abs(sensor.y - y)
        if distance <= sensor_radius:
            diff = abs(sensor_radius - distance)
            return Range(sensor.x - diff, sensor.x + diff)

    def get_coverage_in_line(self, y: int) -> list[Range]:
        ranges = set()
        for sensor in self.sensors:
            new = self.get_sensor_coverage_at_line(sensor, y)
            if new:
                ranges.add(new)

        ranges = sorted(ranges, key=lambda r: r.min)
        merged_ranges = [ranges[0]]
        for current in ranges[1:]:
            previous = merged_ranges[-1]
            if (current.min - 1) <= previous.max:
                merged_ranges.pop()
                merged_ranges.append(previous + current)
            else:
                merged_ranges.append(current)
        return merged_ranges

    def sensor_outline(self, sensor: Point, window: Range) -> typing.Iterator[Point]:
        """ Within grid window, generate all points just outside of the sensor coverage,
        that have manhattan distance from sensor 1 higher than it's radius """

        radius = self.sensor_radius[sensor]
        # Find the bounds of the grid where the sensor is
        min_x = max(window.min, sensor.x - radius)
        max_x = min(window.max, sensor.x + radius)
        min_y = max(window.min, sensor.y - radius)
        max_y = min(window.max, sensor.y + radius)
        # define corner points
        top = Point(0, min_y)
        left = Point(min_x, 0)
        bottom = Point(0, max_y)
        right = Point(max_x, 0)

        # TODO
        yield None

    def get_adjacent_sensors(self) -> list[Point]:
        """ adjacent sensor is such that there is exactly one pixel distance between their borders """


@timeit
def parse(input_file: Path) -> Grid:
    sensors = set()
    beacons = set()
    radius = dict()
    data = input_file.read_text().splitlines()
    # Sensor at x=20, y=1: closest beacon is at x=15, y=3
    for line in data:
        sx, sy, bx, by = re.findall(r'-?\d+', line)
        sensor = Point(int(sx), int(sy))
        beacon = Point(int(bx), int(by))
        sensor_radius = sensor.get_manhattan_distance(beacon)
        sensors.add(sensor)
        beacons.add(beacon)
        radius[sensor] = sensor_radius
    grid = Grid(sensors=list(sensors), beacons=list(beacons), sensor_radius=radius)
    return grid


# part 1
@timeit
def run_sensors(grid: Grid, y: int) -> int:
    beacon_counter = 0
    for beacon in grid.beacons:
        if beacon.y == y:
            beacon_counter += 1
    coverage = sum(len(r) for r in grid.get_coverage_in_line(y))
    return coverage - beacon_counter


def test_run_sensors():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    count = run_sensors(grid, y=TEST_LINE)
    assert count == 26


# part 2
def get_tuning_freq(grid: Grid, beacon_range: Range) -> int:
    beacon = Point(14, 11)
    # TODO
    return beacon.x * FREQ_MULTIPLIER + beacon.y


def test_get_tuning_freq():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    assert get_tuning_freq(grid, TEST_BEACON_RANGE) == 14 * FREQ_MULTIPLIER + 11


def main():
    input_file = HERE / INPUT_FILE
    grid = parse(input_file)
    coverage = run_sensors(deepcopy(grid), y=INPUT_LINE)
    print(f'On line {INPUT_LINE} amount of sensor coverage is: {coverage} ')

    beacon_freq = get_tuning_freq(grid, BEACON_RANGE)
    print(f'Beacon tuning frequency is: {beacon_freq} ')


if __name__ == "__main__":
    main()
