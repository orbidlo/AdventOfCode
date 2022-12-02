# https://adventofcode.com/2022/day/2

import typing
from enum import Enum
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()


class Outcome(Enum):
    DRAW = 3
    WIN = 6
    LOSE = 0


class Move(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


# indexes encode distance of the moves needed for the outcome
OUTCOME = [member.value for member in Outcome]

MOVE_TRANSLATE = dict.fromkeys(['A', 'X'], Move.ROCK) | \
                 dict.fromkeys(['B', 'Y'], Move.PAPER) | \
                 dict.fromkeys(['C', 'Z'], Move.SCISSORS)
OUTCOME_TRANSLATE = {
    'X': Outcome.LOSE,
    'Y': Outcome.DRAW,
    'Z': Outcome.WIN
}


def eval_score(elf_shape: str, my_shape: str) -> int:
    """ Evaluate both shapes for outcome and return score """
    my_move = MOVE_TRANSLATE[my_shape]
    elf_move = MOVE_TRANSLATE[elf_shape]
    distance = my_move.value - elf_move.value
    outcome = Outcome(OUTCOME[distance])
    return my_move.value + outcome.value


def eval_outcome(elf_shape: str, outcome_str: str) -> int:
    """ Evaluate my shape from outcome and return score """
    outcome = OUTCOME_TRANSLATE[outcome_str]
    elf_move = MOVE_TRANSLATE[elf_shape]
    distance = OUTCOME.index(outcome.value)
    my_move = Move((elf_move.value + distance - 1) % 3 + 1)
    return my_move.value + outcome.value


def read_and_eval(input_file: Path, myfunc: typing.Callable[[str, str], int]) -> int:
    rounds_score = []
    for entry in input_file.read_text().splitlines():
        params = entry.split()
        rounds_score.append(myfunc(*params))
    return sum(rounds_score)


# part 1
def get_score(input_file: Path) -> int:
    score = read_and_eval(input_file, eval_score)
    return score


def test_get_score():
    test_score = get_score(HERE / INPUT_TEST)
    assert test_score == 15


# part 2
def get_score_from_outcome(input_file: Path) -> int:
    score = read_and_eval(input_file, eval_outcome)
    return score


def test_get_score_from_outcome():
    test_score = get_score_from_outcome(HERE / INPUT_TEST)
    assert test_score == 12


if __name__ == "__main__":
    final_score = get_score(HERE / INPUT_FILE)
    print(f'Following the guide for your move would get you score  {final_score}.')

    final_score_from_outcome = get_score_from_outcome(HERE / INPUT_FILE)
    print(f'Following the required outcome would get you score  {final_score_from_outcome}.')
