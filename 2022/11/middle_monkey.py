# https://adventofcode.com/2022/day/11

from __future__ import annotations

import math
import operator
import pytest
import re
import time
import typing
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()
ROUNDS = 20
ROUNDS_BIG = 10000


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


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class Monkeys(dict[int, 'Monkey']):

    def __repr__(self) -> str:
        return_str = ''
        for idx, monkey in self.items():
            items = ', '.join(str(item) for item in monkey.items)
            return_str += f'Monkey {idx}: ' + items + '\n'
        return return_str

    def throw_at(self, item: int, target_idx: int) -> None:
        self[target_idx].add_item(item)

    def do_round(self, decrease_func: typing.Callable[[int], int]) -> None:
        for idx in self:
            for item, target_idx in self[idx].inspect(decrease_func):
                self.throw_at(item, target_idx)


@dataclass
class Monkey:
    id: int
    operator: typing.Callable[[int, int], int]
    _operands: list[str]
    divisible: int
    throw_at: tuple[int, int]
    items: list[int] = field(default_factory=list)
    counter: int = 0

    def add_item(self, item: int) -> None:
        self.items.append(item)

    def inspect(self, decrease_func: typing.Callable[[int], int]) -> typing.Iterator[tuple[int, int]]:
        while self.items:
            threat = self.items.pop(0)
            self.counter += 1
            parsed_operands = []
            for str_operand in self._operands:
                if str_operand == 'old':
                    parsed_operands.append(threat)
                else:
                    parsed_operands.append(int(str_operand))
            new_threat = self.operator(*parsed_operands)
            # reduce threat
            new_threat = decrease_func(new_threat)
            yield new_threat, self.throw_at[new_threat % self.divisible == 0]


def parse(input_file: Path) -> Monkeys:
    lines = input_file.read_text().splitlines()
    monkeys = Monkeys()
    for chunk in chunks(lines, 7):
        idx = re.findall(r'\d+', chunk[0])[0]
        operation_lst = chunk[2].strip().split()
        operands = [operation_lst[3], operation_lst[5]]
        if operation_lst[4] == '*':
            operation = operator.mul
        elif operation_lst[4] == '+':
            operation = operator.add
        else:
            raise RuntimeError
        divisible = chunk[3].strip().split()[3]
        true_idx = chunk[4].strip().split()[-1]
        false_idx = chunk[5].strip().split()[-1]
        monkey = Monkey(
            id=int(idx),
            operator=operation,
            _operands=operands,
            divisible=int(divisible),
            throw_at=(int(false_idx), int(true_idx)),
        )
        for item in re.findall(r'\d+', chunk[1]):
            monkey.add_item(int(item))
        monkeys[int(idx)] = monkey
    return monkeys


# part 1
@timeit
def compute_monkey_business(monkeys: Monkeys, rounds: int, decrease_func: typing.Callable[[int], int]) -> int:
    for i in range(rounds):
        monkeys.do_round(decrease_func)
    counts = sorted((monkey.counter for _, monkey in monkeys.items()), reverse=True)
    return counts[0] * counts[1]


@pytest.mark.parametrize(
    "rounds,decrease_worry,expected", [
        (ROUNDS, True, 10605),
        (ROUNDS_BIG, False, 2713310158)
    ])
def test_compute_monkey_business(rounds: int, decrease_worry: bool, expected: int):
    input_file = HERE / INPUT_TEST
    monkeys = parse(input_file)
    if decrease_worry:
        decrease_func = lambda x: x // 3
    else:
        operand = math.prod(monkey.divisible for monkey in monkeys.values())
        decrease_func = lambda x: x % operand
    monkey_business = compute_monkey_business(monkeys, rounds, decrease_func)
    assert monkey_business == expected


def main():
    input_file = HERE / INPUT_FILE
    monkeys = parse(input_file)
    monkey_business = compute_monkey_business(monkeys, ROUNDS, lambda x: x // 3)
    print(f'After {ROUNDS} rounds, the level of monkey business is {monkey_business}.')

    monkeys = parse(input_file)
    operand = math.prod(monkey.divisible for monkey in monkeys.values())
    monkey_business = compute_monkey_business(monkeys, ROUNDS_BIG, lambda x: x % operand)
    print(f'After {ROUNDS_BIG} rounds, the level of monkey business is {monkey_business}.')


if __name__ == "__main__":
    main()
