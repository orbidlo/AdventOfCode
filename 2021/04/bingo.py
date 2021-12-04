# https://adventofcode.com/2021/day/4

import os
import itertools
import logging

from typing import Optional
from dataclasses import dataclass, field

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@dataclass
class Bingo:
    """ Class for keeping track of Bingo boards """
    rows: list[list[int]]
    cols: list[list[int]] = field(init=False)
    id: int = field(default_factory=itertools.count().__next__, init=False)

    def __post_init__(self):
        if len(self.rows) != 5:
            raise ValueError(f'Incorrect number of rows: {len(self.rows)} is not 5')
        self.cols = [list(col) for col in zip(*self.rows)]
        # self.cols = [[row[i] for row in self.rows] for i in range(5)]

    def total_sum(self) -> int:
        """ Returns total sum of all remaining numbers in bingo board. """
        return sum(itertools.chain.from_iterable(self.rows))

    def strike_number(self, number) -> Optional[int]:
        """ Will strike the number from bingo board. """
        for line in itertools.chain(self.rows, self.cols):
            while number in line:
                line.remove(number)
            if not line:  # list is empty
                logging.debug(f'BINGO! After removing {number}, there is an empty line!\n'
                              f'Total count of remaining numbers is {self.total_sum()}.')
                return self.total_sum() * number
        return None


def parse_lines(input_file) -> (list[int], list[Bingo]):
    all_rows = []
    boards = []

    with open(input_file) as f:
        numbers = [int(x) for x in f.readline().strip().split(sep=',')]

        for line in f:
            line = line.strip()
            if line:
                all_rows.append([int(x) for x in line.split()])

    for rows in chunks(all_rows, 5):
        boards.append(Bingo(rows))

    return numbers, boards


# part 1
def calculate_bingo(input_file) -> Optional[int]:
    numbers, boards = parse_lines(input_file)
    for number in numbers:
        for board in boards:
            score = board.strike_number(number)
            if score is not None:
                return score
    return None


def test_calculate_bingo():
    test_score = calculate_bingo(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_score == 4512


# part 2
def calculate_last_winning_bingo(input_file) -> Optional[int]:
    numbers, boards = parse_lines(input_file)

    for number in numbers:
        logging.debug(f'\nStriking number {number}.')
        score = None
        for i, board in enumerate(boards[:]):
            logging.debug(f'\tRunning board {board.id}.')
            score = board.strike_number(number)
            logging.debug(f'\t\tRows: {board.rows}\n\t\tCols: {board.cols}.')
            if score is not None:
                boards.pop(i)
                logging.debug(f'Board {board.id} has won with score {score} and will be skipped.')
        if not boards:
            return score
    return None


def test_calculate_last_winning_bingo():
    test_score = calculate_last_winning_bingo(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_score == 1924


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    final_score = calculate_bingo(INPUT_FILE)
    logging.info(f'Your final score for first board is {final_score}.')

    final_last_score = calculate_last_winning_bingo(INPUT_FILE)
    logging.info(f'Your final score for last board is {final_last_score}.')
