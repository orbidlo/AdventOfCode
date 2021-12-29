# https://adventofcode.com/2021/day/24

from __future__ import annotations

import logging
import operator
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from timeit import default_timer as timer

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


@dataclass
class NaiveAlu:
    """
        Proof of concept ALU for running parsed commands over model number.
        Cannot be used as it would mean trying out 9^14 candidate numbers.
    """
    model_number: str
    commands: list[list[str]]
    variables: dict[str, int] = field(default_factory=dict, init=False)
    input: Iterator[int] = field(init=False)
    translate = {
        'add': operator.add,
        'mul': operator.mul,
        'div': operator.floordiv,
        'mod': operator.mod,
        'eql': operator.eq
    }

    def __post_init__(self) -> None:
        self.variables = {
            'w': 0,
            'x': 0,
            'y': 0,
            'z': 0
        }
        assert self.model_number.isdigit()
        self.input = (int(char) for char in self.model_number)

    def compute(self, command: str, a: str, b: str = None):
        if command == 'inp':
            self.variables[a] = next(self.input)
            return
        if command not in self.translate:
            raise ValueError(f'Command {command} is not supported!')
        b = to_int(b)
        if isinstance(b, str):
            b = self.variables[b]
        self.variables[a] = int(self.translate[command](self.variables[a], b))

    def run_commands(self) -> None:
        for command in self.commands:
            self.compute(*command)

    def is_valid(self) -> bool:
        return self.variables['z'] == 0


def to_int(num: str) -> str | int:
    try:
        return int(num)
    except ValueError:
        return num


def parse_file(input_file: str) -> list[list]:
    """ Parse input file into list of commands. """
    commands = []
    with open(input_file) as f:
        for line in f:
            commands.append(line.strip().split())
    return commands


@dataclass
class Alu:
    """
    Optimized ALU which uses logic extracted from MONAD input.
    Input can be translated into:
        w = int(input())
        x = int((z % 26) + b != w)
        z //= a
        z *= 25*x+1
        z += (w+c)*x

        for a == 1
            x = 1
            z //= 1
            z *= 26
            z += w+c
        -> z is stack and pushing into it w+c in base 26.

        -> we need to pop everything so z = 0 at the end
        for a == 26:
            x = 0
            z //= 26
            (z % 26) + b == w -> prev_w + prev_c + curr_b = curr_w
    """
    commands: list[list]

    def compute(self, inp: list[int]) -> list[int]:
        stack = []
        for curr in range(14):
            b = int(self.commands[18 * curr + 5][-1])
            c = int(self.commands[18 * curr + 15][-1])

            if b > 0:
                # z = z // 1 -> push
                stack += [(curr, c)]
                continue
            # z = z // 26 -> pop
            prev, c = stack.pop()

            inp[curr] = inp[prev] + b + c
            # correct if we are outside of range of digits 1-9
            if inp[curr] > 9:
                inp[prev] -= inp[curr] - 9
                inp[curr] = 9
            if inp[curr] < 1:
                inp[prev] += 1 - inp[curr]
                inp[curr] = 1
        return inp

    def get_lowest(self) -> str:
        lowest = [1] * 14
        return ''.join(str(c) for c in self.compute(lowest))

    def get_highest(self) -> str:
        highest = [9] * 14
        return ''.join(str(c) for c in self.compute(highest))


def test_naive_alu():
    number = '56'
    commands = [
        ['inp', 'w'], ['inp', 'x'], ['add', 'x', 3], ['mul', 'w', 'x'],
        ['mod', 'w', '20'], ['div', 'w', '2'], ['eql', 'w', '2']
    ]
    naive_alu = NaiveAlu(model_number=number, commands=commands)
    naive_alu.run_commands()
    assert naive_alu.variables['w'] == 1


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    alu = Alu(parse_file(INPUT_FILE))
    start_time = timer()
    final_highest_number = alu.get_highest()
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final highest valid number is {final_highest_number}.')

    start_time = timer()
    final_lowest_number = alu.get_lowest()
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final lowest valid number is {final_lowest_number}.')
