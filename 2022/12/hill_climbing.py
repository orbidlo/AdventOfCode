# https://adventofcode.com/2022/day/12

from __future__ import annotations

import string
import typing
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path
from queue import PriorityQueue
from typing import Iterator

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()
ROUNDS = 20
ROUNDS_BIG = 10000
TRANSLATE = string.ascii_lowercase

Point = namedtuple('Point', ['x', 'y'])


@dataclass
class Grid:
    """ Graph with edge weights, neighbors suitable for Dijkstra algorithm. Capable of enlargement. """
    elevation: list[list[int]]
    start: Point
    end: Point
    solved_points: set = field(default_factory=set, init=False)  # structure for storing already solved vertices

    @property
    def width(self) -> int:
        return len(self.elevation[0])

    @property
    def height(self) -> int:
        return len(self.elevation)

    def __eq__(self, other: Grid) -> bool:
        return self.elevation == other.elevation

    def __len__(self) -> int:
        return self.width * self.height

    def __getitem__(self, point: Point) -> int | None:
        """ Get edge weight for target point. """
        return self.elevation[point.y][point.x]

    def __repr__(self) -> str:
        return '\n' + '\n'.join(str(row) for row in self.elevation)

    def is_within_boundary(self, point: Point) -> bool:
        """ Test if given point fits within grid boundary. """
        return (0 <= point.x < self.width) and (0 <= point.y < self.height)

    def get_neighbors(self, point: Point, inverted: bool = False) -> typing.Iterator[Point]:
        """ For given point generate valid adjacent points within grid boundary. """
        for adj in [Point(point.x + x, point.y + y) for x, y in [(0, -1), (1, 0), (0, 1), (-1, 0)]]:
            # adjacent point must be within boundary and with at most 1 higher elevation, or 1 lower if inverted
            if self.is_within_boundary(adj):
                if (not inverted and self[adj] - self[point] <= 1) or (inverted and self[point] - self[adj] <= 1):
                    yield adj

    def all_points(self) -> Iterator[Point]:
        """ Generate all points within graph. """
        for x in range(self.width):
            for y in range(self.height):
                yield Point(x, y)


@timeit
def parse(input_file: Path) -> tuple[Grid, list[Point]]:
    """ Parse input file for graph representation. """
    data = input_file.read_text().splitlines()
    parsed = []
    start, end, val = None, None, None
    lowest_elevations = []
    for y, line in enumerate(data):
        row = []
        for x, char in enumerate(list(line.strip())):
            if char == 'S':
                start = Point(x, y)
                lowest_elevations.append(start)
                val = TRANSLATE.index('a')
            elif char == 'E':
                end = Point(x, y)
                val = TRANSLATE.index('z')
            elif char == 'a':
                lowest_elevations.append(Point(x, y))
                val = TRANSLATE.index(char)
            else:
                val = TRANSLATE.index(char)
            row.append(val)
        parsed.append(row)
    grid = Grid(parsed, start, end)
    return grid, lowest_elevations


def a_star(graph: Grid, start_point: Point, end_point: Point | None) -> dict[Point, int]:
    """ A* algorithm for finding all shortest paths from start within given graph using priority queue (distance). """

    graph.solved_points = set()
    shortest_path: dict[Point, int | None] = {point: None for point in graph.all_points()}

    # start by adding the distance to the starting point, which is zero
    shortest_path[start_point] = 0
    # we create priority queue sorted by distance to the current point
    priority_queue: PriorityQueue[tuple[int, Point]] = PriorityQueue()
    # at the beginning we put inside only the starting point with distance = 0
    priority_queue.put((0, start_point))
    # calculate the shortest path for all the points in queue
    while not priority_queue.empty():
        # remove current point from priority queue
        current_distance, current = priority_queue.get()
        # add current point to solved set
        graph.solved_points.add(current)
        # solve all it's neighbors
        for neighbor in graph.get_neighbors(current, inverted=end_point is None):
            # edge weight is always 1 as we generate only acceptable neighbors
            distance = 1
            # skip this neighbor if it's already solved
            if neighbor in graph.solved_points:
                continue
            # get previously stored distance for this neighbor
            old_cost = shortest_path[neighbor]
            # calculate new distance for neighbor using edge from current point
            new_cost = current_distance + distance
            # if new distance is shorter or old distance is not yet calculated
            if not old_cost or new_cost < old_cost:
                # store the new shortest distance for the neighbor
                shortest_path[neighbor] = new_cost
                # if we found end, stop algorithm
                if neighbor == end_point:
                    break
                # place the neighbor into priority queue so all it's neighbors can be solved as well
                priority_queue.put((new_cost, neighbor))

    # return shortest paths for all paths starting in starting point
    return shortest_path


# part 1
@timeit
def find_shortest_path(grid: Grid) -> int:
    paths = a_star(graph=grid, start_point=grid.start, end_point=grid.end)
    return paths[grid.end]


def test_find_shortest_path():
    input_file = HERE / INPUT_TEST
    grid, _ = parse(input_file)
    assert find_shortest_path(grid) == 31


# part 2
@timeit
def find_shortest_path_from_any_start(grid: Grid, lowest_elevations: list[Point]) -> int:
    # to find all shortest paths from any start with the lowest elevation to the end:
    # start in grid.end and find all accessible paths and then check shortest paths to the lowest elevations
    paths = a_star(graph=grid, start_point=grid.end, end_point=None)
    return min(paths[end] for end in lowest_elevations if paths[end] is not None)


def test_find_shortest_path_from_any_start():
    input_file = HERE / INPUT_TEST
    grid, all_lowest_elevations = parse(input_file)
    assert find_shortest_path_from_any_start(grid, all_lowest_elevations) == 29


def main():
    input_file = HERE / INPUT_FILE
    grid, lowest_elevations = parse(input_file)
    shortest_path = find_shortest_path(grid)
    print(f'Shortest path from start to end takes {shortest_path} valid steps. ')

    shortest_path_from_any_start = find_shortest_path_from_any_start(grid, lowest_elevations)
    print(f'Shortest path from any start to end takes {shortest_path_from_any_start} valid steps. ')


if __name__ == "__main__":
    main()
