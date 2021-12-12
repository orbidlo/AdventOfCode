# https://adventofcode.com/2021/day/12

from __future__ import annotations

from timeit import default_timer as timer
from dataclasses import dataclass, field
from collections import defaultdict, Counter

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

START_NODE = 'start'
END_NODE = 'end'


def can_visit(node: str, path: list, only_once: bool) -> bool:
    """ Logic to determine how many times we can visit node in graph """
    # cave is big or on yet visited
    if not node.islower() or node not in path:
        result = True
    # cave is start or end and already visited
    elif node in (START_NODE, END_NODE):
        result = False
    # cave is small and already visited - and can be only once
    elif only_once:
        result = False
    # cave is small, already visited but can be visited twice once
    else:
        lower_count = Counter(v for v in path if v.islower())
        result = bool(2 not in lower_count.values())
    return result


@dataclass
class Graph:
    """ Class for non-oriented graph that can find all paths from A to B """
    graph: defaultdict[str, list[str]] = field(default_factory=lambda: defaultdict(list), init=False)

    @classmethod
    def parse_lines(cls, input_file: str) -> Graph:
        """ Get Graph from input file """
        graph = cls()
        with open(input_file) as f:
            for line in f:
                [a, b] = line.strip().split('-')
                graph.add_edge(a, b)
        return graph

    def add_edge(self, a: str, b: str):
        """ Adds edge to the graph. """
        self.graph[a].append(b)
        self.graph[b].append(a)

    def find_all_paths(self, start: str, end: str, path: list[str], only_once: bool = True) -> list[list[str]]:
        """ Find all paths between start and end nodes, allow more complex logic with can_visit() function """
        # add start node to path
        path = path + [start]
        # we reached end and can return path
        if start == end:
            return [path]
        # there is no way to continue, return empty path
        if start not in self.graph:
            return []
        # get all paths that continue from starting node
        paths = []
        for node in self.graph[start]:
            # check that we can visit node given existing path
            if can_visit(node, path, only_once):
                new_paths = self.find_all_paths(node, end, path, only_once)
                for new_path in new_paths:
                    paths.append(new_path)

        return paths


# part 1
def count_paths(input_file: str) -> int:
    graph = Graph.parse_lines(input_file)
    paths = graph.find_all_paths(START_NODE, END_NODE, [])
    return len(paths)


def test_count_paths():
    test_count = count_paths(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 226


# part 2

def count_paths_twice(input_file: str) -> int:
    graph = Graph.parse_lines(input_file)
    paths = graph.find_all_paths(START_NODE, END_NODE, [], only_once=False)
    return len(paths)


def test_count_paths_twice():
    test_count = count_paths_twice(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_count == 3509


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    total_count = count_paths(INPUT_FILE)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) Number of paths from {START_NODE} to {END_NODE} '
                 f'(small node can be visited only once) is {total_count}.')

    start_time = timer()
    total_count = count_paths_twice(INPUT_FILE)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) Number of paths from {START_NODE} to {END_NODE} '
                 f'(small node can be visited twice once) is {total_count}.')
