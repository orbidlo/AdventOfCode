# https://adventofcode.com/2022/day/2

import typing
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()

# A for Rock, B for Paper, and C for Scissors
# score: 1 for Rock, 2 for Paper, and 3 for Scissors
# outcome: 0: lost, 3: draw, and 6: win

ELF_SCORE = {'A': 1, 'B': 2, 'C': 3}
MY_SCORE = {'X': 1, 'Y': 2, 'Z': 3}
OUTCOME = {'X': 0, 'Y': 3, 'Z': 6}

# distance is difference between my and elf score wrapped around 1-2-3-1
OUTCOME_DISTANCE = {0: 2, 3: 0, 6: 1}


def wrap(number: int, increment: int, maximum: int) -> int:
    """ Add increment to number but beyond maximum wrap it from 1 again. """
    return (number + increment - 1) % maximum + 1


def eval_score(elf_shape: str, my_shape: str) -> int:
    """ Evaluate both shapes for outcome and return score """
    my_score = MY_SCORE[my_shape]
    elf_score = ELF_SCORE[elf_shape]
    outcome = None
    for score, distance in OUTCOME_DISTANCE.items():
        if my_score == wrap(elf_score, distance, 3):
            outcome = score
    assert outcome is not None
    return my_score + outcome


def eval_outcome(elf_shape: str, outcome_str: str) -> int:
    """ Evaluate my shape from outcome and return score """
    outcome = OUTCOME[outcome_str]
    elf_score = ELF_SCORE[elf_shape]
    assert outcome in OUTCOME_DISTANCE.keys()
    my_score = wrap(elf_score, OUTCOME_DISTANCE[outcome], 3)

    return my_score + outcome


def read_and_eval(input_file: Path, myfunc: typing.Callable[[str, str], int]) -> list[int]:
    rounds_score = []
    for guide in input_file.read_text().splitlines():
        rounds_score.append(myfunc(*tuple(guide.split())))
    return rounds_score


# part 1
def get_score(input_file: Path) -> int:
    score = read_and_eval(input_file, eval_score)
    return sum(score)


def test_get_score():
    test_score = get_score(HERE / INPUT_TEST)
    assert test_score == 15


# part 2
def get_score_from_outcome(input_file: Path) -> int:
    score = read_and_eval(input_file, eval_outcome)
    return sum(score)


def test_get_score_from_outcome():
    test_score = get_score_from_outcome(HERE / INPUT_TEST)
    assert test_score == 12


if __name__ == "__main__":
    final_score = get_score(HERE / INPUT_FILE)
    print(f'Following the guide for your move would get you score  {final_score}.')

    final_score_from_outcome = get_score_from_outcome(HERE / INPUT_FILE)
    print(f'Following the required outcome would get you score  {final_score_from_outcome}.')
