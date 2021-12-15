# https://adventofcode.com/2021/day/15

from __future__ import annotations

import logging
import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from queue import PriorityQueue
from timeit import default_timer as timer
from typing import Iterator

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'
INPUT_TEST2 = 'input_test2.txt'

WEIGHT_CAP = 9
ENLARGEMENT_COEF = 5

Point = namedtuple('Point', 'x y')


@dataclass
class Graph:
    """ Graph with edge weights, neighbors suitable for Dijkstra algorithm. Capable of enlargement. """

    risk_level: list[list[int]]  # grid representation with edge weights stored under target point
    solved_points: set = field(default_factory=set, init=False)  # structure for storing already solved vertices

    @property
    def width(self) -> int:
        return len(self.risk_level[0])

    @property
    def height(self) -> int:
        return len(self.risk_level)

    def get_end_point(self) -> Point:
        """ Get end point which is on bottom right of grid. """
        return Point(self.width - 1, self.height - 1)

    def __eq__(self, other: Graph) -> bool:
        return self.risk_level == other.risk_level

    def __len__(self) -> int:
        return self.width * self.height

    def __getitem__(self, vertex: Point) -> int | None:
        """ Get edge weight for target vertex. """
        return self.risk_level[vertex.y][vertex.x]

    def __repr__(self) -> str:
        return '\n' + '\n'.join(str(row) for row in self.risk_level)

    def is_within_boundary(self, point: Point) -> bool:
        """ Test if given point fits within grid boundary. """
        return (0 <= point.x < self.width) and (0 <= point.y < self.height)

    def get_neighbors(self, point: Point) -> Point:
        """ For given point generate adjacent points within grid boundary. """
        for adj in [Point(point.x + x, point.y + y) for x, y in {(0, -1), (1, 0), (0, 1), (-1, 0)}]:
            if self.is_within_boundary(adj):
                yield adj

    def all_points(self) -> Iterator[Point]:
        """ Generate all points within graph. """
        for x in range(self.width):
            for y in range(self.height):
                yield Point(x, y)

    def enlarge(self, coefficient: int):
        """ Enlarge graph by copying existing grid but raising the risk levels. """
        def raise_risk(input_row: list[int], times: int) -> list[int]:
            """ Raises risk for whole row. """
            return [x + times if x + times <= WEIGHT_CAP else x + times - WEIGHT_CAP for x in input_row]

        # add more columns
        large_rows = []
        for row in self.risk_level:
            large_row = []
            for i in range(0, coefficient):
                large_row += raise_risk(row, times=i)
            large_rows.append(large_row)

        # add more rows
        for i in range(1, coefficient):
            for large_row in large_rows[0:len(self.risk_level)]:
                large_rows.append(raise_risk(large_row, times=i))

        self.risk_level = large_rows


def parse_lines(input_file: str) -> Graph:
    """ Parse input file for graph representation. """
    rows = []
    with open(input_file) as f:
        for line in f:
            if line.strip():
                rows.append([int(x) for x in list(line.strip())])

    graph = Graph(rows)
    return graph


def dijkstra(graph: Graph, start_vertex: Point) -> dict[Point, int]:
    """ Dijkstra's algorithm for finding all shortest paths from start within given graph. """

    graph.solved_points = set()
    shortest_path: dict[Point, int | None] = {point: None for point in graph.all_points()}

    # start by adding the distance to the starting vertex, which is zero
    shortest_path[start_vertex] = 0
    # we create priority queue sorted by distance to the current vertex
    priority_queue: PriorityQueue[tuple[int, Point]] = PriorityQueue()
    # at the beginning we put inside only the starting vertex with weight = 0
    priority_queue.put((0, start_vertex))
    # calculate the shortest path for all the points in queue
    while not priority_queue.empty():
        # remove current vertex from priority queue
        current_distance, current_vertex = priority_queue.get()
        # add current vertex to solved set
        graph.solved_points.add(current_vertex)
        # solve all it's neighbors
        for neighbor in graph.get_neighbors(current_vertex):
            # get edge weight between current vertex and it's neighbor
            distance = graph[neighbor]
            # skip this neighbor if it's already solved
            if neighbor in graph.solved_points:
                continue
            # get previously stored distance for this neighbor
            old_cost = shortest_path[neighbor]
            # calculate new distance for neighbor using edge from current vertex
            new_cost = current_distance + distance
            # if new distance is shorter or old distance is not yet calculated
            if not old_cost or new_cost < old_cost:
                # store the new shortest distance for the neighbor
                shortest_path[neighbor] = new_cost
                # place the neighbor into priority queue so all it's neighbors can be solved as well
                priority_queue.put((new_cost, neighbor))

    # return shortest paths for all paths starting in starting vertex
    return shortest_path


# part 1
def get_total_risk(graph: Graph) -> int:
    """ Get total risk level of the shortest path from start to end """
    risks = dijkstra(graph=graph, start_vertex=Point(0, 0))
    return risks[graph.get_end_point()]


def test_get_total_risk():
    test_risk = get_total_risk(graph=parse_lines(os.path.join(os.path.dirname(__file__), INPUT_TEST)))
    assert test_risk == 40


# part 2
def test_graph_enlarging():
    large_graph = parse_lines(os.path.join(os.path.dirname(__file__), INPUT_TEST2))
    graph = parse_lines(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    graph.enlarge(coefficient=ENLARGEMENT_COEF)
    assert large_graph == graph
    test_large_risk = get_total_risk(graph=graph)
    assert test_large_risk == 315


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    final_graph = parse_lines(INPUT_FILE)

    start_time = timer()
    total_risk = get_total_risk(graph=final_graph)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Risk level of shortest path is {total_risk}.')

    start_time = timer()
    final_graph.enlarge(coefficient=ENLARGEMENT_COEF)
    total_risk = get_total_risk(graph=final_graph)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Risk level of shortest path for enlarged graph is {total_risk}.')
