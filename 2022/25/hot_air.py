# https://adventofcode.com/2022/day/25

from __future__ import annotations

from pathlib import Path

import pytest

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()

TO_DEC = {
    '2': 2,
    '1': 1,
    '0': 0,
    '-': -1,
    '=': -2
}

FROM_DEC = ['0', '1', '2', '=', '-']


def snafu_to_dec(snafu: str) -> int:
    res = 0
    for char in snafu:
        res *= 5
        res += TO_DEC[char]
    return res


def dec_to_snafu(dec_number: int) -> str:
    snafu = ''
    dec = dec_number
    while dec > 0:
        char = FROM_DEC[dec % 5]
        if char in ('-', '='):
            dec += 5
        snafu = char + snafu
        dec //= 5
    if dec:
        snafu = FROM_DEC[dec] + snafu
    return snafu


@timeit
def parse(input_file: Path) -> list[str]:
    data = input_file.read_text().splitlines()
    return data


@timeit
def get_snafu_number(numbers: list[str]) -> str:
    return dec_to_snafu(sum(snafu_to_dec(num) for num in numbers))


def test_get_snafu_number():
    input_file = HERE / INPUT_TEST
    numbers = parse(input_file)
    answer = get_snafu_number(numbers)
    assert answer == '2=-1=0'


@pytest.mark.parametrize(
    "snafu,dec", [
        ('1', 1),
        ('2', 2),
        ('1=', 3),
        ('1-', 4),
        ('10', 5),
        ('11', 6),
        ('12', 7),
        ('2=', 8),
        ('2-', 9),
        ('20', 10),
        ('1=0', 15),
        ('1-0', 20),
        ('1=11-2', 2022),
        ('1-0---0', 12345),
        ('1121-1110-1=0', 314159265),
    ])
def test_conversions(snafu, dec):
    assert snafu_to_dec(snafu) == dec
    assert snafu == dec_to_snafu(dec)


def main():
    input_file = HERE / INPUT_FILE
    numbers = parse(input_file)
    answer = get_snafu_number(numbers)
    print(f'SNAFU number is: {answer}')


if __name__ == "__main__":
    main()
