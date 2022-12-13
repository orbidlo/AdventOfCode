# https://adventofcode.com/2022/day/13

from __future__ import annotations

from ast import literal_eval
from dataclasses import dataclass
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, chunks

HERE = Path(__file__).parent.resolve()


@dataclass
class Packet:
    value: list[Packet] | list[int] | int | None

    def __repr__(self):
        return str(self.value)

    def __lt__(self, other: Packet) -> bool:
        if isinstance(self.value, int) and isinstance(other.value, int):
            return self.value < other.value
        if isinstance(self.value, list) and isinstance(other.value, list):
            for left, right in zip(self.value, other.value):
                if left == right or [left] == right or left == [right]:
                    continue
                return Packet(left) < Packet(right)
            return len(self.value) < len(other.value)
        if isinstance(self.value, int) and isinstance(other.value, list):
            return Packet([self.value]) < other
        if isinstance(self.value, list) and isinstance(other.value, int):
            return self < Packet([other.value])


Pair = tuple[Packet, Packet]


@timeit
def parse(input_file: Path) -> list[Pair]:
    pairs = []
    for pair in chunks(input_file.read_text().splitlines(), 3):
        pairs.append((Packet(literal_eval(pair[0])), Packet(literal_eval(pair[1]))))
    return pairs


# part 1
@timeit
def check_right_order(pairs: list[Pair]) -> int:
    return sum(idx for idx, (left, right) in enumerate(pairs, start=1) if left < right)


def test_check_right_order():
    input_file = HERE / INPUT_TEST
    pairs = parse(input_file)
    assert check_right_order(pairs) == 13


# part 2
@timeit
def sort_packets(pairs: list[Pair]) -> int:
    marker = Packet([[2]]), Packet([[6]])
    pairs.append(marker)
    packets = [item for pair in pairs for item in pair]
    packets.sort()
    return (packets.index(marker[0]) + 1) * (packets.index(marker[1]) + 1)


def test_sort_packets():
    input_file = HERE / INPUT_TEST
    pairs = parse(input_file)
    assert sort_packets(pairs) == 140


def main():
    input_file = HERE / INPUT_FILE
    pairs = parse(input_file)
    right_order = check_right_order(pairs)
    print(f'Sum of indices of all pairs that are in right order is {right_order} ')

    decoder_key = sort_packets(pairs)
    print(f'Decoder key for distress signal is {decoder_key}')


if __name__ == "__main__":
    main()
