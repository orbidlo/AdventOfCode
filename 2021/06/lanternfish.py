# https://adventofcode.com/2021/day/6

from dataclasses import dataclass
from collections import Counter
from timeit import default_timer as timer

import sys
import os
import logging
import numpy as np

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

NEWBORN_CD = 8  # reproduction countdown for newly born fish
RESET_CD = 6  # reproduction countdown for fish that just created offspring


@dataclass
class FishPopulation:
    """ This represents all the lantern-fish in the ocean """
    countdown_counter: Counter  # counter of all the fish using their reproduction countdown as key

    def size(self):
        """ Size of current fish population. """
        return sum(self.countdown_counter.values())

    def cd_subtract(self):
        """ Simulates one day passing and how it affects the fish. """
        new_cd_counter = Counter()
        # for all the fish subtract one day from their countdown
        for key, val in self.countdown_counter.items():
            new_cd_counter[key - 1] = val
        # negative countdown means those fish are currently reproducing
        reproducing = new_cd_counter.get(-1)
        if reproducing:
            # create newborn fish
            new_cd_counter[NEWBORN_CD] += reproducing
            # reset fish
            new_cd_counter[RESET_CD] += reproducing
            del new_cd_counter[-1]
        self.countdown_counter = new_cd_counter

    def advance(self, days: int) -> None:
        """ Advance population by number of days given. """
        for _ in range(days):
            self.cd_subtract()


def parse_lines(input_file) -> list[int]:
    with open(input_file) as f:
        parsed = [int(x) for x in f.readline().strip().split(',')]
    return parsed


# part 1
def simulate_fish(input_file: str, days: int) -> int:
    fish = parse_lines(input_file)
    arr = np.array(fish)
    while days > 0:
        new = np.repeat(NEWBORN_CD, np.count_nonzero(arr == 0))
        arr = arr - 1
        arr[arr < 0] = RESET_CD
        arr = np.append(arr, new)
        days -= 1
    return arr.size


def test_simulate_fish():
    test_count = simulate_fish(os.path.join(os.path.dirname(__file__), INPUT_TEST), days=80)
    assert test_count == 5934


# part 2

def simulate_hella_lot_fish(input_file: str, days: int) -> int:
    parsed = parse_lines(input_file)
    fish = FishPopulation(Counter(parsed))
    fish.advance(days)

    return fish.size()


def test_simulate_hella_lot_fish():
    test_count = simulate_hella_lot_fish(os.path.join(os.path.dirname(__file__), INPUT_TEST), days=256)
    assert test_count == 26984457539


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    count = simulate_fish(INPUT_FILE, days=80)
    end = timer()
    logging.info(f'({end - start:.2}s elapsed) Total count of lantern-fish after 80 days is {count}.')

    start = timer()
    hella_count = simulate_hella_lot_fish(INPUT_FILE, days=256)
    end = timer()
    logging.info(f'({end - start:.2}s elapsed) Total count of lantern-fish after 256 days is {hella_count}.')
