# https://adventofcode.com/2021/day/17

from __future__ import annotations

import logging
import os
import re
import sys
from collections import namedtuple, defaultdict
from dataclasses import dataclass, field
from timeit import default_timer as timer

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

Point = namedtuple('Point', 'x y')
Velocity = namedtuple('Velocity', 'x y')
START_TRAJECTORY = Point(0, 0)


def move_to_zero(x: int) -> int:
    """ Move x coordinate to zero and return it. """
    if x == 0:
        return x
    if x < 0:
        return x + 1
    return x - 1


def sum_of_finite_series(distance) -> int:
    """ Calculate sum of finite series for given distance (distance + distance-1 + ... + 1 + 0). """
    return (distance * (distance + 1)) // 2


def grow_trajectory(current_point: Point, current_velocity: Velocity) -> tuple[Point, Velocity]:
    """ Grow trajectory according to given rules and return new point and velocity. """
    # grow trajectory by velocity
    new_point_x = current_point.x + current_velocity.x
    new_point_y = current_point.y + current_velocity.y
    # lessen velocity by drag and gravity
    new_velocity_x = move_to_zero(current_velocity.x)
    new_velocity_y = current_velocity.y - 1
    return Point(new_point_x, new_point_y), Velocity(new_velocity_x, new_velocity_y)


@dataclass
class Grid:
    """ Class for describing grid with target area and possible trajectories generated within. """
    coordinates: tuple[tuple[int, int], tuple[int, int]]  # input coordinates = (x1,x2), (y1,y2)
    # target area definition
    target_min: Point = field(init=False)  # leftmost upper point of target area
    target_max: Point = field(init=False)  # rightmost lower point of target area
    # all trajectories that have any point in target area defined above
    trajectories: dict[Velocity, list[Point]] = field(default_factory=lambda: defaultdict(list), init=False)

    def __post_init__(self):
        x_coordinates, y_coordinates = self.coordinates
        self.target_min = Point(min(x_coordinates), min(y_coordinates))
        self.target_max = Point(max(x_coordinates), max(y_coordinates))

    def in_area_x(self, x: int) -> bool:
        """ Given x-coordinate is within target area. """
        if self.target_min.x <= x <= self.target_max.x:
            return True
        return False

    def in_area_y(self, y: int) -> bool:
        """ Given y-coordinate is within target area. """
        if self.target_min.y <= y <= self.target_max.y:
            return True
        return False

    def trajectory_in_area(self, trajectory: list[Point]) -> bool:
        """ Return True if given trajectory is within target area. """
        for point in trajectory:
            if self.in_area_x(point.x) and self.in_area_y(point.y):
                return True
        return False

    def overshot(self, point: Point, velocity: Velocity) -> bool:
        """ For given point and velocity decide if this overshoots target area with no chance of reaching it. """
        # falling straight down and not within area x-coordinate
        if velocity.x == 0 and not self.in_area_x(point.x):
            return True
        # still growing in both coordinates but beyond target area
        if point.x > self.target_max.x or point.y < self.target_min.y:
            return True
        return False

    def generate_trajectory(self, start_velocity: Velocity) -> list[Point]:
        """ Generate trajectory for given velocity and return it. """
        trajectory = [START_TRAJECTORY]
        curr_point, curr_velocity = grow_trajectory(START_TRAJECTORY, current_velocity=start_velocity)
        while not self.overshot(curr_point, curr_velocity):
            trajectory.append(curr_point)
            curr_point, curr_velocity = grow_trajectory(curr_point, current_velocity=curr_velocity)
        return trajectory

    def find_trajectories(self):
        """ Find all trajectories that go through target area and store them by their starting velocity. """
        for x in range(1, self.target_max.x + 1):
            for y in range(-1 * abs(self.target_min.y - 0), abs(self.target_min.y - 0)):
                velocity = Velocity(x, y)
                new_trajectory = self.generate_trajectory(velocity)
                if self.trajectory_in_area(new_trajectory):
                    self.trajectories[velocity] = new_trajectory


def parse_file(input_file: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """ Parse input file for range of x-coordinates and y-coordinates. """
    with open(input_file) as f:
        line = f.readline()

    match = re.search(r'x=(?P<x1>[-\d]+)\.\.(?P<x2>[-\d]+), y=(?P<y1>[-\d]+)\.\.(?P<y2>[-\d]+)', line)
    x_range = int(match.group('x1')), int(match.group('x2'))
    y_range = int(match.group('y1')), int(match.group('y2'))
    return x_range, y_range


# part 1
def find_max_height(y_coordinates: tuple[int, int]) -> int:
    """
        Find max height we can reach from starting velocity while still hitting target area.

        To find max height, we can explore only the behaviour of y-coordinates. This is reasoning:
        We need to find such initial velocity that the speed of falling is maximum possible.
        Maximum height/speed of falling is reached for leftmost lower point of target area
            where velocity.x=0 (falling straight down) we can always find velocity.x such that it targets desired area
            - that is velocity.x * (velocity.x + 1) // 2 in range(target_min_x, target_max_x + 1)
        Due to velocity.y always decreasing constantly, we will need to fall through y=0 and max distance is thus
            velocity.y + 1 = abs(target_min_y - 0)
        Max height is then computed as sum of finite series: velocity.y + velocity.y-1 + ... + 1
    """
    velocity_y = abs(min(y_coordinates) - 0) - 1
    return sum_of_finite_series(velocity_y)


def test_find_max_height():
    _, ys = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_velocity = find_max_height(ys)
    assert test_velocity == 45


# part 2
def count_all_velocities(grid: Grid) -> int:
    """ Generate valid trajectories hitting target area and return their count. """
    grid.find_trajectories()
    return len(grid.trajectories.keys())


def test_count_all_velocities():
    test_coords = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_count = count_all_velocities(Grid(test_coords))
    assert test_count == 112


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    _, y_coords = parse_file(INPUT_FILE)
    total_velocity = find_max_height(y_coords)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Highest y position achieved is {total_velocity}.')

    start_time = timer()
    coords = parse_file(INPUT_FILE)
    sum_velocity = count_all_velocities(Grid(coords))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Sum of all valid starting velocities is {sum_velocity}.')
