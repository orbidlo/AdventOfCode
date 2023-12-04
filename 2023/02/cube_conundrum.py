# https://adventofcode.com/2023/day/2

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()


@dataclass
class Cubes:
    red: int = 0
    green: int = 0
    blue: int = 0


CUBES_MAX = Cubes(red=12, green=13, blue=14)


@dataclass
class Game:
    game_id: int
    max_red: int = 0
    max_green: int = 0
    max_blue: int = 0

    def update_max(self, cubes: Cubes) -> None:
        if cubes.red > self.max_red:
            self.max_red = cubes.red
        if cubes.green > self.max_green:
            self.max_green = cubes.green
        if cubes.blue > self.max_blue:
            self.max_blue = cubes.blue

    def get_power(self) -> int:
        return self.max_red * self.max_green * self.max_blue

    def is_possible(self, limit: Cubes) -> bool:
        return self.max_red <= limit.red and self.max_green <= limit.green and self.max_blue <= limit.blue

    @classmethod
    def parse_game(cls, line: str) -> Game:
        game, line_rounds = line.split(":")
        game_id = int(game.split()[1])
        game = cls(game_id)
        for r in line_rounds.split(";"):
            cubes = Cubes(0, 0, 0)
            for c in r.split(","):
                num, color = c.split()
                setattr(cubes, color, int(num))
            game.update_max(cubes)
        return game


def parse_file(input_file: Path) -> dict[int, Game]:
    data = input_file.read_text().splitlines()
    games = dict()
    for line in data:
        game = Game.parse_game(line)
        games[game.game_id] = game
    return games


# part 1
@timeit
def possible_games(games: dict[int, Game], limit: Cubes) -> list[int]:
    possible_ids = [game_id for game_id, game in games.items() if game.is_possible(limit)]
    return possible_ids


def test_possible_games():
    test_games = parse_file(HERE / INPUT_TEST)
    test_games_ids = possible_games(test_games, CUBES_MAX)
    assert sum(test_games_ids) == 8


# part 2
@timeit
def fewest_cubes_power(games: dict[int, Game]) -> list[int]:
    power = [game.get_power() for game in games.values()]
    return power


def test_fewest_cubes():
    test_games = parse_file(HERE / INPUT_TEST)
    test_power = fewest_cubes_power(test_games)
    assert sum(test_power) == 2286


if __name__ == "__main__":
    final_games = parse_file(HERE / INPUT_FILE)

    final_ids = possible_games(final_games, CUBES_MAX)
    print(f"Sum of all possible games is: {sum(final_ids)}")

    final_power = fewest_cubes_power(final_games)
    print(f"Sum of a power of fewest cubes per game is s: {sum(final_power)}")
