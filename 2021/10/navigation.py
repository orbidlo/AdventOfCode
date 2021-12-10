# https://adventofcode.com/2021/day/10

from timeit import default_timer as timer

import sys
import os
import logging

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

ERROR_SCORE = {
    ')': 3,
    ']': 57,
    '}': 1197,
    '>': 25137
}
PAIRS = dict((a, b) for a, b in ("()", "[]", "{}", "<>"))


def parse_lines(input_file) -> list[str]:
    lines = []
    with open(input_file) as f:
        for line in f:
            lines.append(line.strip())
    return lines


def check_syntax(line: str, stack: list) -> int:
    """ Check line syntax and return error score."""
    for char in line:
        if char in PAIRS.keys():
            stack.append(PAIRS[char])
        elif stack[-1] == char:
            stack.pop()
        else:
            logging.debug(f'Found illegal {char} instead of {stack[-1]}')
            return ERROR_SCORE[char]
    return 0


# part 1
def get_error_score(input_file: str) -> int:
    """ Get sum of error codes for whole file """
    lines = parse_lines(input_file)
    error_score = 0
    for line in lines:
        stack = []
        error_score += check_syntax(line, stack)
    return error_score


def test_get_error_score():
    error_score = get_error_score(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert error_score == 26397


# part 2
def get_autocomplete_score(input_file: str) -> int:
    """ Get middle autocomplete score for all incomplete but valid lines in file. """
    lines = parse_lines(input_file)
    scores = []
    for line in lines:
        stack = []
        score = 0
        err = check_syntax(line, stack)
        if not err:
            for elem in reversed(stack):
                score *= 5
                score += list(PAIRS.values()).index(elem) + 1
        if score:
            scores.append(score)
    scores.sort()
    return scores[len(scores) // 2]


def test_get_autocomplete_score():
    test_score = get_autocomplete_score(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_score == 288957


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start = timer()
    total_err_score = get_error_score(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Sum of syntax error score for invalid lines is {total_err_score}.')

    start = timer()
    total_auto_score = get_autocomplete_score(INPUT_FILE)
    end = timer()
    logging.info(f'({end - start:.4f}s elapsed) Middle autocompletion score for valid lines is {total_auto_score}.')
