# https://adventofcode.com/2022/day/3
import string
import typing as t
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()

N = 3  # number of lines in each group


def get_priority(letter: str) -> int:
    assert len(letter) == 1
    return string.ascii_letters.index(letter) + 1


def split_each_line_in_half(data: list[str]) -> t.Iterable[tuple[str]]:
    for line in data:
        half = len(line) // 2
        yield line[:half], line[half:]


def split_every_nth_line(data: list[str]) -> t.Iterable[tuple[str]]:
    iterators = [iter(data)] * N
    return zip(*iterators)


def find_intersection(data: t.Iterable[tuple[str]]) -> int:
    priorities = []
    for groups in data:
        set_groups = (set(s) for s in groups)
        intersection = set.intersection(*set_groups)
        assert len(intersection) == 1
        priorities.append(get_priority(intersection.pop()))
    return sum(priorities)


# part 1
@timeit
def get_priorities(input_file: Path) -> int:
    data = input_file.read_text().splitlines()
    priorities = find_intersection(split_each_line_in_half(data))
    return priorities


def test_get_priorities():
    test_priorities = get_priorities(HERE / INPUT_TEST)
    assert test_priorities == 157


# part 2
@timeit
def get_common_priorities(input_file: Path) -> int:
    data = input_file.read_text().splitlines()
    priorities = find_intersection(split_every_nth_line(data))
    return priorities


def test_get_common_priorities():
    test_priorities = get_common_priorities(HERE / INPUT_TEST)
    assert test_priorities == 70


if __name__ == "__main__":
    final_priority = get_priorities(HERE / INPUT_FILE)
    print(f'Sum of priorities for each rucksack halves intersection is  {final_priority}.')

    final_common_priority = get_common_priorities(HERE / INPUT_FILE)
    print(f'Sum of priorities for every three rucksacks intersection is {final_common_priority}.')
