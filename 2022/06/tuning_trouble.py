# https://adventofcode.com/2022/day/6

from __future__ import annotations

from pathlib import Path

import pytest

from libs import timeit, INPUT_FILE

HERE = Path(__file__).parent.resolve()

PACKET_LENGTH = 4
MESSAGE_LENGTH = 14


@timeit
def parse_input(input_file: Path) -> str:
    data = input_file.read_text().strip()
    return data


# part 1 & 2
@timeit
def find_mark(stream: str, length: int) -> int:
    for counter in range(length, len(stream)):
        if len(set(stream[counter - length:counter])) == length:
            return counter
    raise RuntimeError('No marker found!')


@pytest.mark.parametrize(
    "stream,packet_mark,message_mark", [
        ('mjqjpqmgbljsphdztnvjfqwrcgsmlb', 7, 19),
        ('bvwbjplbgvbhsrlpgdmjqwftvncz', 5, 23),
        ('nppdvjthqldpwncqszvftbrmjlhg', 6, 23),
        ('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg', 10, 29),
        ('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw', 11, 26)
    ])
def test_find_marker(stream, packet_mark, message_mark):
    assert packet_mark == find_mark(stream, PACKET_LENGTH)
    assert message_mark == find_mark(stream, MESSAGE_LENGTH)


def main():
    stream = parse_input(HERE / INPUT_FILE)

    packet_mark = find_mark(stream, PACKET_LENGTH)
    print(f'Number of characters that need to be processed to find first start-of-packet marker is {packet_mark}.')

    message_mark = find_mark(stream, MESSAGE_LENGTH)
    print(f'Number of characters that need to be processed to find first start-of-message marker is {message_mark}.')


if __name__ == "__main__":
    main()
