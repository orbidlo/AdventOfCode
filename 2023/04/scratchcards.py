# https://adventofcode.com/2023/day/4

from collections import Counter
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()


def parse_file(input_file: Path) -> list[tuple]:
    cards = []
    for line in input_file.read_text().splitlines():
        _, numbers = line.split(":")
        winning, my_numbers = numbers.split("|")
        winning = set(winning.split())
        my_numbers = set(my_numbers.split())
        cards.append((winning, my_numbers))
    return cards


def get_points(number: int) -> int:
    if number == 0:
        return 0
    return 2 ** (number - 1)


# part 1
@timeit
def calculate_card_points(cards: list[tuple]) -> int:
    total_points = 0
    for winning, my_numbers in cards:
        intersection = my_numbers.intersection(winning)
        total_points += get_points(len(intersection))
    return total_points


def test_calculate_card_points():
    data = parse_file(HERE / INPUT_TEST)
    test_points = calculate_card_points(data)
    assert test_points == 13


# part 2
@timeit
def calculate_copies(cards: list[tuple]) -> int:
    counter = Counter()
    for idx, numbers in enumerate(cards, start=1):
        counter[idx] += 1
        winning_numbers, my_numbers = numbers
        number_of_copies = len(my_numbers.intersection(winning_numbers))
        for i in range(number_of_copies):
            copy_idx = idx + i + 1
            if copy_idx > len(cards):
                break
            counter[copy_idx] += counter[idx]
    return counter.total()


def test_calculate_cards():
    data = parse_file(HERE / INPUT_TEST)
    test_cards = calculate_copies(data)
    assert test_cards == 30


if __name__ == "__main__":
    final_data = parse_file(HERE / INPUT_FILE)

    final_points = calculate_card_points(final_data)
    print(f"Sum of all card points: {final_points}")

    final_copies = calculate_copies(final_data)
    print(f"Number of all cards and their copies: {final_copies}")
