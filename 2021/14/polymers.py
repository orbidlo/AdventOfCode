# https://adventofcode.com/2021/day/14

from __future__ import annotations

import itertools
import logging
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from timeit import default_timer as timer
from typing import Protocol

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def parse_lines(input_file: str) -> tuple[list, dict]:
    """ Parse input file for polymer template and insertion rules. """
    rules = dict()
    with open(input_file) as f:
        polymers = list(f.readline().strip())
        for line in f:
            if line.strip():
                pair, insert_char = line.strip().split(' -> ')
                assert len(pair) == 2, f'rule: {pair} must be two character long'
                assert len(insert_char) == 1, f'rule: {insert_char} must be one character long'
                rules[tuple(pair)] = insert_char
    return polymers, rules


class PolymerProtocol(Protocol):
    """ Represent polymer template modification protocol based on insertion rules. """

    def __len__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...

    def step(self) -> None:
        """ Apply all insertion rules into polymer template. """
        ...

    def get_counts(self) -> tuple[int, int]:
        """ Return counts of most common letter and least common letter in polymer template. """
        ...


@dataclass
class Polymers(PolymerProtocol):
    """ Implements PolymerProtocol. Polymer template is stored as list. """
    _init_template: list[str]
    _rules: dict[tuple[str, str], str]

    def __len__(self) -> int:
        return len(self._init_template)

    def __repr__(self) -> str:
        return ''.join(self._init_template)

    @property
    def first_char(self):
        return self._init_template[0]

    @property
    def last_char(self):
        return self._init_template[-1]

    def step(self) -> None:
        new_template = []
        iter_a, iter_b = itertools.tee(self._init_template)
        next(iter_b, None)
        # generate all pairs from two iterators
        for pair in zip(iter_a, iter_b):
            # always append first from pair to template
            new_template.append(pair[0])
            if pair in self._rules:
                # if pair matches rule, insert new character to template
                new_template.append(self._rules[pair])
        # append last character at the end
        new_template.append(self.last_char)
        self._init_template = new_template

    def get_counts(self) -> tuple[int, int]:
        char_counter = Counter(self._init_template)
        char_counts = char_counter.most_common()
        return char_counts[0][1], char_counts[-1][1]


@dataclass
class BigPolymers(PolymerProtocol):
    """ Implements PolymerProtocol. Big polymer template is converted into counter of template pairs. """
    _init_template: list[str]
    _rules: dict[tuple[str, str], str]
    _pairs: Counter = field(init=False)

    @property
    def first_char(self):
        return self._init_template[0]

    @property
    def last_char(self):
        return self._init_template[-1]

    def __post_init__(self):
        self._pairs = Counter(zip(self._init_template, self._init_template[1:]))

    def __len__(self) -> int:
        return sum(self._pairs.values()) + 1

    def __repr__(self) -> str:
        return repr(self._pairs)

    def step(self) -> None:
        new_counter = Counter()
        for pair, char in self._rules.items():
            if pair in self._pairs:
                count = self._pairs.pop(pair)
                new_counter[(pair[0], char)] += count
                new_counter[(char, pair[1])] += count
        self._pairs.update(new_counter)

    def get_counts(self) -> tuple[int, int]:
        char_counter = Counter({self.first_char: 1, self.last_char: 1})
        for pair, count in self._pairs.items():
            char_counter[pair[0]] += count
            char_counter[pair[1]] += count
        char_counts = char_counter.most_common()
        return char_counts[0][1] // 2, char_counts[-1][1] // 2


# part 1
def get_polymer_quantity(polymers: PolymerProtocol, days: int) -> int:
    for day in range(days):
        logging.debug(f'Day {day} - len {len(polymers)}')
        polymers.step()
    most_common_count, least_common_count = polymers.get_counts()
    return most_common_count - least_common_count


def test_get_polymer_quantity():
    polymers = Polymers(parse_lines(os.path.join(os.path.dirname(__file__), INPUT_TEST)))
    test_quantity = get_polymer_quantity(polymers=polymers, days=10)
    assert test_quantity == 1588


def test_get_big_polymer_quantity():
    polymers = BigPolymers(parse_lines(os.path.join(os.path.dirname(__file__), INPUT_TEST)))
    test_quantity = get_polymer_quantity(polymers=polymers, days=40)
    assert test_quantity == 2188189693529


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    big_polymers = BigPolymers(parse_lines(INPUT_FILE))

    start_time = timer()
    quantity = get_polymer_quantity(big_polymers, 10)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Quantity after 10 days is: {quantity}.')

    start_time = timer()
    quantity = get_polymer_quantity(big_polymers, 40)
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Quantity after 40 days is: {quantity}.')
