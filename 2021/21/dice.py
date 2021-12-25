# https://adventofcode.com/2021/day/21

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from functools import cache
from timeit import default_timer as timer

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

NUM_ROLLS = 3
BOARD_POSITIONS = 10
# all 27 possible universes where 3-sided dice was rolled three times, grouped to 7 sums by total score in them
# Counter(sum(elem) for elem in itertools.product(range(1, 4), repeat=NUM_ROLLS))
ROLL_SUMS = {3: 1, 4: 3, 5: 6, 6: 7, 7: 6, 8: 3, 9: 1}


def wrap_number(number: int, increment: int, maximum: int = BOARD_POSITIONS) -> int:
    """ Add increment to number but beyond maximum wrap it from 1 again. """
    return (number + increment - 1) % maximum + 1


def parse_file(input_file: str) -> tuple[int, int]:
    """ Parse given file into two board starting positions. """
    with open(input_file) as f:
        player_1 = f.readline().strip().split()[4]
        player_2 = f.readline().strip().split()[4]

    return int(player_1), int(player_2)


@dataclass
class Dice:
    """ Deterministic dice generating 1,2,3, ... ,100 and then starting from the beginning. """
    sides: int = 100
    position: int = 1

    @classmethod
    def roll(cls) -> int:
        old_position = cls.position
        cls.position = wrap_number(number=cls.position, increment=1, maximum=cls.sides)
        return old_position


@dataclass
class Player:
    """
        Deterministic player rolls 3 times the deterministic dice and then moves on the board.
        Where they land, it adds the number to their score.
    """
    position: int
    score: int = 0

    def move(self):
        forward = 0
        for _ in range(NUM_ROLLS):
            forward += Dice.roll()
        self.position = wrap_number(number=self.position, increment=forward)
        self.score += self.position

    def wins(self, max_score: int) -> bool:
        return self.score >= max_score


# part 1
def play_deterministic_dice(players: tuple[Player, Player], max_score: int = 1000) -> tuple[int, int]:
    """ Play deterministic dice for two players until one of them reaches 1000 score. """
    counter = 0
    while True:
        for idx, player in enumerate(players):
            player.move()
            counter += NUM_ROLLS
            if player.wins(max_score):
                return counter, players[0 if idx else 1].score


def test_play():
    pos_1, pos_2 = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    players = (Player(pos_1), Player(pos_2))
    test_counter, score = play_deterministic_dice(players)
    assert test_counter * score == 739785


# part 2
@cache
def play_quantum_dice(position_1: int, position_2: int, score_1: int, score_2: int) -> tuple[int, int]:
    """
        Cached recursive function to play quantum dice.
        Each time player moves, they roll three times. Each roll splits universes to three where player rolled 1,2,3.
        Thus, on each move, 27 universes are created, but are grouped to 7 by their total score and count.
    """
    # atomic scenario within the deepest recursion where it is decided, which player wins this universe
    if score_1 >= 21:
        return 1, 0
    if score_2 >= 21:
        return 0, 1

    total_player_1_wins = 0
    total_player_2_wins = 0

    # each of universe group, containing dirac roll sum and how many universes they contain, splits current status
    for roll_sum, count in ROLL_SUMS.items():
        # compute new position and score for player in position 1
        new_position = wrap_number(position_1, roll_sum)
        new_score = score_1 + new_position
        # store result and swap position to player 2 to play his turn
        player_2_wins, player_1_wins = play_quantum_dice(position_2, new_position, score_2, new_score)
        # to determine total universes in which the player won, their total wins must be multiplied by initial count
        total_player_1_wins += player_1_wins * count
        total_player_2_wins += player_2_wins * count

    return total_player_1_wins, total_player_2_wins


def test_play_quantum_dice():
    test_pos_1, test_pos_2 = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_player_1_wins, _ = play_quantum_dice(test_pos_1, test_pos_2, 0, 0)
    assert test_player_1_wins == 444356092776315


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    player_position_1, player_position_2 = parse_file(INPUT_FILE)
    final_counter, final_score = play_deterministic_dice(players=(Player(player_position_1), Player(player_position_2)))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final result for Deterministic Dice is {final_counter * final_score}.')

    start_time = timer()
    player_position_1, player_position_2 = parse_file(INPUT_FILE)
    total_wins = play_quantum_dice(player_position_1, player_position_2, 0, 0)
    total_winner = max(total_wins)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final result for Dirac Dice is {total_winner} wins.')
