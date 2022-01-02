# https://adventofcode.com/2021/day/23

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from queue import PriorityQueue
from timeit import default_timer as timer
from typing import Iterator


class Amphipod(Enum):
    """ Amphipods and their cost to movement. """
    A = 1
    B = 10
    C = 100
    D = 1000


AMPHIPODS = list(Amphipod)


@dataclass(frozen=True)
class GameState:
    """ Game state (hashable) of Amphipods' locations based on definition: AABBCCDD (or AAAABBBBCCCCDDDD). """
    amps: str
    finished: set = field(hash=False, compare=False)

    def __repr__(self) -> str:
        return ' '.join(location + ':' + self[location].name for location in self.amps)

    def __lt__(self, other: GameState) -> bool:
        return len(self.finished) < len(other.finished)

    def __getitem__(self, item: str) -> Amphipod | None:
        if item not in self:
            return None
        return AMPHIPODS[self.amps.index(item) // (self.count // len(Amphipod))]

    def __contains__(self, item: str) -> bool:
        return item in self.amps

    def __iter__(self) -> Iterator[str]:
        return iter(self.amps)

    @cached_property
    def count(self) -> int:
        return len(self.amps)

    def is_end_state(self) -> bool:
        """ If in current state all Amphipods are in their proper room. """
        return len(self.finished) == self.count


@dataclass
class Graph:
    """
        Graph is map within which Amphipods (defined by their location) are rearranged into individual game states.
        Implements get_neighbor(game_state) which can be used in Dijkstra algorithm to compute the least costly order
        of movements needed to rearrange Amphipods into their proper room.
        Locations just outside of room, that cannot be occupied, are skipped so adjacent locations gain double cost.
    """
    hallway: str  # locations within hallway
    crossroad: str  # locations on the crossroads with room entrance
    movement: dict[str, str]  # movement definition (graph edges)
    rooms: dict[Amphipod, str]  # definition of destination location for given Amphipod

    def make_state(self, definition: str) -> GameState:
        """
            Create game state along with set of finished locations which already have right Amphipod in it.
            Game state definition is sorted alphabetically in each room part to merge equivalent states.
        """
        definition_len = len(definition)
        amps_count = len(Amphipod)
        assert definition_len % amps_count == 0
        n = definition_len // amps_count
        sorted_def = [''.join(sorted(definition[idx: idx + n])) for idx in range(0, definition_len, n)]
        finished = set()
        # confirm which Amphipods are in correct location while not blocking another
        for room, def_room in zip(self.rooms.values(), sorted_def):
            for location in reversed(room):
                if location not in def_room:
                    break
                finished.add(location)
        return GameState(''.join(sorted_def), finished)

    def move_amp(self, state: GameState, old_loc: str, new_loc: str) -> GameState:
        """ Create new game state by moving Amphipod into new location. """
        assert new_loc not in state, "Cannot move to location already filled!"
        idx = state.amps.index(old_loc)
        new_amps = state.amps[:idx] + new_loc + state.amps[idx + 1:]
        return self.make_state(new_amps)

    def get_cost(self, start: str, end: str) -> int | None:
        """ Get cost of atomic movement between two locations. """
        if start in self.crossroad and end in self.crossroad:
            return 2
        return 1

    def has_clear_room(self, state: GameState, amp: Amphipod) -> bool:
        """ If given Amphipod can move to its destination room (not filled by wrong Amphipod). """
        for location in self.rooms[amp]:
            if location in state and state[location] != amp:
                return False
        return True

    def generate_movement(self, state: GameState, location: str) -> Iterator[tuple[str, int]]:
        """ For Amphipod defined by its location generate valid movement and cost to adjacent game states.  """
        amp = state[location]
        # get proper target of movement for Amphipod in given location based on it's position
        if location not in self.hallway:
            target = self.hallway
        elif self.has_clear_room(state, amp):
            target = self.rooms[amp]
        else:
            # exit as we cannot move anywhere
            return
        valid_paths = {location: 0}
        queue = [location]
        # use DFS to calculate all paths and their cost, possible because graph of movements is a tree
        while queue:
            current = queue.pop(0)
            for adjacent in self.movement[current]:
                if adjacent in state:
                    # skip movement that is blocked
                    continue
                if adjacent not in valid_paths:
                    valid_paths[adjacent] = valid_paths[current] + self.get_cost(current, adjacent)
                    queue.append(adjacent)
        for end, cost in valid_paths.items():
            # yield only paths that have proper target, cost is multiplied by Amphipods' movement cost
            if end in target:
                yield end, cost * amp.value

    def get_neighbors(self, state: GameState) -> Iterator[tuple[GameState, int]]:
        """ Generate all legal states and their cost from given game state.  """
        for location in state:
            if location in state.finished:
                # skip Amphipods that are already in their destination
                continue
            for movement in self.generate_movement(state, location):
                new_location, cost = movement
                yield self.move_amp(state, location, new_location), cost


HALLWAY = '1234567'

# #############
# #12.3.4.5.67#
# ###a#c#e#g###
#   #b#d#f#h#
#   #########


CROSSROAD = '23456aceg'
MOVEMENT: dict[str, str] = {
    'a': '23b',
    'b': 'a',
    'c': '34d',
    'd': 'c',
    'e': '45f',
    'f': 'e',
    'g': '56h',
    'h': 'g',
    '1': '2',
    '2': '13a',
    '3': '24ac',
    '4': '35ce',
    '5': '46eg',
    '6': '75g',
    '7': '6',
}
ROOMS = {
    Amphipod.A: 'ab',
    Amphipod.B: 'cd',
    Amphipod.C: 'ef',
    Amphipod.D: 'gh',
}

GRAPH = Graph(HALLWAY, CROSSROAD, MOVEMENT, ROOMS)

# #############
# #...........#
# ###B#C#B#D###
#   #A#D#C#A#
#   #########

TEST_STATE = GRAPH.make_state('bhaecfdg')

# #############
# #...........#
# ###B#A#B#C###
#   #C#D#D#A#
#   #########

STATE = GRAPH.make_state('chaebgdf')

# #############
# #12.3.4.5.67#
# ###a#e#i#m###
#   #b#f#j#n#
#   #c#g#k#o#
#   #d#h#l#p#
#   #########

CROSSROAD2 = '23456aeim'
MOVEMENT2: dict[str, str] = {
    'a': '23b',
    'b': 'ac',
    'c': 'bd',
    'd': 'c',
    'e': '34f',
    'f': 'eg',
    'g': 'fh',
    'h': 'g',
    'i': '45j',
    'j': 'ki',
    'k': 'jl',
    'l': 'k',
    'm': '56n',
    'n': 'mo',
    'o': 'np',
    'p': 'o',
    '1': '2',
    '2': '13a',
    '3': '24ae',
    '4': '35ei',
    '5': '46im',
    '6': '75m',
    '7': '6',
}
ROOMS2 = {
    Amphipod.A: 'abcd',
    Amphipod.B: 'efgh',
    Amphipod.C: 'ijkl',
    Amphipod.D: 'mnop',
}

GRAPH2 = Graph(HALLWAY, CROSSROAD2, MOVEMENT2, ROOMS2)

# #############
# #...........#
# ###B#C#B#D###
#   #D#C#B#A#
#   #D#B#A#C#
#   #A#D#C#A#
#   #########

TEST_STATE2 = GRAPH2.make_state('dknpagijeflobchm')

# #############
# #...........#
# ###B#A#B#C###
#   #D#C#B#A#
#   #D#B#A#C#
#   #C#D#D#A#
#   #########

STATE2 = GRAPH2.make_state('eknpagijdfmobchl')


def dijkstra(graph: Graph, start_state: GameState) -> dict[GameState, int]:
    """ Dijkstra's algorithm for finding all shortest paths from start within given graph. """
    solved_states = set()
    # start by adding the distance to the starting vertex, which is zero
    shortest_path: dict[GameState, int | None] = {start_state: 0}
    # we create priority queue sorted by distance to the current vertex
    priority_queue: PriorityQueue[tuple[int, GameState]] = PriorityQueue()
    # at the beginning we put inside only the starting vertex with weight = 0
    priority_queue.put((0, start_state))
    # calculate the shortest path for all the points in queue
    while not priority_queue.empty():
        # remove current vertex from priority queue
        current_distance, current_state = priority_queue.get()
        # exit if we already found end state
        if current_state.is_end_state():
            return {current_state: current_distance}
        # add current vertex to solved set
        solved_states.add(current_state)
        # solve all it's neighbors with their distances
        for neighbor, distance in graph.get_neighbors(state=current_state):
            # skip this neighbor if it's already solved
            if neighbor in solved_states:
                continue
            # get previously stored distance for this neighbor, get None if none exists
            old_cost = shortest_path.get(neighbor, None)
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
def get_least_expensive_path(graph: Graph, start_state: GameState) -> int:
    paths = dijkstra(graph, start_state)
    return min(cost for state, cost in paths.items() if state.is_end_state())


def test_get_least_expensive_path():
    test_energy = get_least_expensive_path(GRAPH, TEST_STATE)
    assert test_energy == 12521


def test_get_least_expensive_path_2():
    test_energy = get_least_expensive_path(GRAPH2, TEST_STATE2)
    assert test_energy == 44169


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    least_energy = get_least_expensive_path(GRAPH, STATE)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Least energy needed to rearrange amphipods in part 1 is {least_energy}.')

    start_time = timer()
    least_energy = get_least_expensive_path(GRAPH2, STATE2)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Least energy needed to rearrange amphipods in part 2 is {least_energy}.')
