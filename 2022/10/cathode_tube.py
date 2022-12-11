# https://adventofcode.com/2022/day/10

from __future__ import annotations

import time
import typing
from dataclasses import dataclass
from functools import wraps
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()

CYCLES = [20, 60, 100, 140, 180, 220]
CRT_WIDTH = 40
CRT_HEIGHT = 6


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        total_time = end_time - start_time
        print(f'\tFunction {func.__name__} took {total_time / 1000} μs')
        return result

    return timeit_wrapper


def chunks(iterable: list | str, n: int) -> typing.Iterator[list | str]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


@dataclass
class CPU:
    _register: int = 1
    _cycle: int = 0
    crt: str = ''

    def __repr__(self) -> str:
        return '\n'.join(chunks(self.crt, CRT_WIDTH)) + '\n'

    def run_instruction(self, instruction: str) -> typing.Iterator[int]:
        match instruction.strip().split():
            case ['noop']:
                yield self.tick()
            case ['addx', number]:
                yield self.tick()
                yield self.tick()
                self._register += int(number)

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def sprite(self) -> tuple[int, int, int]:
        middle = self._register
        return middle - 1, middle, middle + 1

    @property
    def signal_strength(self) -> int:
        return self._register * self._cycle

    def draw_pixel(self) -> None:
        symbol = '.'
        if (self.cycle % CRT_WIDTH) in self.sprite:
            symbol = '#'
        self.crt += symbol

    def tick(self) -> int:
        for i in range(CRT_WIDTH * CRT_HEIGHT):
            self.draw_pixel()
            self._cycle += 1
            return self.signal_strength


# part 1
@timeit
def compute_signal_strength(cpu: CPU, instructions: list[str]) -> int:
    signals = []
    for instruction in instructions:
        for signal in cpu.run_instruction(instruction):
            if cpu.cycle in CYCLES:
                signals.append(signal)

    return sum(signals)


# part 2
def draw_crt(cpu: CPU, instructions: list[str]) -> None:
    for instruction in instructions:
        for _ in cpu.run_instruction(instruction):
            if cpu.cycle == (CRT_WIDTH * CRT_HEIGHT):
                return


def test_draw_crt():
    expected = """\
##..##..##..##..##..##..##..##..##..##..\
###...###...###...###...###...###...###.\
####....####....####....####....####....\
#####.....#####.....#####.....#####.....\
######......######......######......####\
#######.......#######.......#######.....\
"""
    input_file = HERE / INPUT_TEST
    lines = input_file.read_text().splitlines()
    cpu = CPU()
    draw_crt(cpu, lines)
    assert cpu.crt == expected


def main():
    input_file = HERE / INPUT_FILE
    lines = input_file.read_text().splitlines()
    cpu = CPU()
    signal = compute_signal_strength(cpu, lines)
    print(f'Sum of signal strengths is {signal}.')

    cpu = CPU()
    draw_crt(cpu, lines)
    print(f'\nCRT shows this:\n' + repr(cpu))


if __name__ == "__main__":
    main()
