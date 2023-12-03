# https://adventofcode.com/2023/day/2
import re
from collections import namedtuple
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from libs import timeit, to_int, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()

Cubes = namedtuple('Cubes', ['red', 'green', 'blue'])


@dataclass
class Cubes:
    red: int = 0
    green: int = 0
    blue: int = 0

    def __gt__(self, other) -> bool:
        return self.red > other.red or self.green > other.green or self.blue > other.blue

    def set_max(self, other: Cubes) -> None:
        if other.red > self.red:
            self.red = other.red
        if other.green > self.green:
            self.green = other.green
        if other.blue > self.blue:
            self.blue = other.blue

    def get_power(self) -> int:
        return self.red * self.green * self.blue


CUBES_MAX = Cubes(red=12, green=13, blue=14)


# Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
def parse_games(input_file: Path) -> dict[int, list[Cubes]]:
    games = {}
    for line in input_file.read_text().splitlines():
        game, line_rounds = line.split(':')
        game_id = int(game.split()[1])
        rounds = []
        for r in line_rounds.split(';'):
            cubes = Cubes()
            for c in r.split(','):
                num, color = c.split()
                if hasattr(cubes, color):
                    setattr(cubes, color, int(num))
            rounds.append(cubes)
        games[game_id] = rounds
    return games


def get_possible_games(games, limit) -> list[int]:
    possible = []
    for game_id, game_cubes in games.items():
        is_possible = True
        for cubes in game_cubes:
            if cubes > limit:
                is_possible = False
                break
            if not is_possible:
                break
        if is_possible:
            possible.append(game_id)
    return possible


def get_fewest_cubes(games) -> list[int]:
    power_of_max_cubes = []
    for game_id, game_cubes in games.items():
        max_cubes = Cubes(0, 0, 0)
        for cubes in game_cubes:
            max_cubes.set_max(cubes)
        power_of_max_cubes.append(max_cubes.get_power())
    return power_of_max_cubes


# part 1
@timeit
def possible_games(input_file: Path) -> list[int]:
    games = parse_games(input_file)
    possible_ids = get_possible_games(games, CUBES_MAX)
    return possible_ids


def test_possible_games():
    test_games_ids = possible_games(HERE / INPUT_TEST)
    assert sum(test_games_ids) == 8


# part 2
@timeit
def fewest_cubes_power(input_file: Path) -> list[int]:
    games = parse_games(input_file)
    power = get_fewest_cubes(games)
    return power


def test_fewest_cubes():
    test_power = fewest_cubes_power(HERE / INPUT_TEST)
    assert sum(test_power) == 2286


if __name__ == "__main__":
    final_ids = possible_games(HERE / INPUT_FILE)
    print(f'Sum of all possible games is: {sum(final_ids)}')

    final_power = fewest_cubes_power(HERE / INPUT_FILE)
    print(f'Sum of a power of fewest cubes per game is s: {sum(final_power)}')
