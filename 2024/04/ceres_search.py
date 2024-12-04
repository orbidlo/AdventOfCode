# https://adventofcode.com/2024/day/4

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from libs import timeit, INPUT_FILE, INPUT_TEST, Point

HERE = Path(__file__).parent.resolve()
DIRS = {Point(0, -1), Point(1, -1), Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0), Point(-1, -1)}
X_SHAPE_DIRS = {Point(1, -1), Point(1, 1), Point(-1, 1), Point(-1, -1)}
XMAS = ["X", "M", "A", "S"]


@dataclass
class Grid:
    """
    Represents a 2D grid of characters for word searching.
    This class stores the grid data and provides efficient access to letter coordinates.
    """

    data: list[str]
    letter_coordinates: dict[str, set[Point]] = field(default_factory=lambda: defaultdict(set), init=False)

    def __repr__(self) -> str:
        return "\n".join(self.data)

    def __post_init__(self):
        self.words = defaultdict(set)
        for y, line in enumerate(self.data):
            for x, letter in enumerate(line):
                self.letter_coordinates[letter].add(Point(x, y))


def parse_file(input_file: Path) -> Grid:
    result = input_file.read_text().splitlines()
    return Grid(result)


# part 1
@timeit
def count_word(grid: Grid, word: list[str]) -> int:
    """ Counts the number of times a word can be found in the grid. """
    counter = 0
    for start in grid.letter_coordinates[word[0]]:
        for d in DIRS:
            if all(start + d * i in grid.letter_coordinates[word[i]] for i in range(1, len(word))):
                counter += 1
    return counter


def test_count_xmas():
    test_grid = parse_file(HERE / INPUT_TEST)
    xmas_counter = count_word(test_grid, XMAS)
    assert xmas_counter == 18


# part 2
@timeit
def count_x_mas(grid: Grid) -> int:
    """ Counts the number of times an X shaped MAS can be found in the grid. """
    # find MAS word, store the coordinate of middle letter and direction
    for middle in grid.letter_coordinates["A"]:
        for direction in X_SHAPE_DIRS:
            if (
                middle - direction in grid.letter_coordinates["M"]
                and middle + direction in grid.letter_coordinates["S"]
            ):
                grid.words[middle].add(direction)
    # count only those MAS words that share the same middle and form X shape
    return sum(1 for word in grid.words.values() if len(word) == 2)


def test_count_x_mas():
    test_grid = parse_file(HERE / INPUT_TEST)
    x_mas_counter = count_x_mas(test_grid)
    assert x_mas_counter == 9


if __name__ == "__main__":
    final_grid = parse_file(HERE / INPUT_FILE)

    final_counter = count_word(final_grid)
    print(f"Count of XMAS is: {final_counter}")

    final_counter = count_x_mas(final_grid)
    print(f"Count of X-MAS is: {final_counter}")
