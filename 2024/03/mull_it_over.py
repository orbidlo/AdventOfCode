# https://adventofcode.com/2024/day/3

from __future__ import annotations

import re
from pathlib import Path
from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()
INPUT_TEST2 = "input_test2.txt"
PATTERN = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)|" 
                     r"do\(\)|" 
                     r"don't\(\)")


def parse_file(input_file: Path) -> str:
    return input_file.read_text()


# part 1
@timeit
def get_multiplication_result(corrupted_data: str) -> int:
    """ Return the sum of multiplication results from the data."""
    products = (
        int(match.group(1)) * int(match.group(2))
        for match in re.finditer(PATTERN, corrupted_data)
        if 'mul' in match.group(0)
    )
    return sum(products)


def test_get_multiplication_result():
    test_data = parse_file(HERE / INPUT_TEST)
    test_safe_reports = get_multiplication_result(test_data)
    assert test_safe_reports == 161


# part 2
@timeit
def get_enabled_results(corrupted_data: str) -> int:
    """Return the sum of enabled results from the data."""
    result = 0
    enabled = True
    for match in re.finditer(PATTERN, corrupted_data):
        if match.group(0).startswith("don't"):
            enabled = not enabled
        elif match.group(0).startswith("do"):
            enabled = True
        if match.group(0).startswith("mul") and enabled:
            result += int(match.group(1)) * int(match.group(2))
    return result


def test_get_enabled_results():
    test_data = parse_file(HERE / INPUT_TEST2)
    test_enabled_results = get_enabled_results(test_data)
    assert test_enabled_results == 48


if __name__ == "__main__":
    final_data = parse_file(HERE / INPUT_FILE)

    final_result = get_multiplication_result(final_data)
    print(f"Multiplication results added: {final_result}")

    final_result = get_enabled_results(final_data)
    print(f"Enabled multiplication results added: {final_result}")
