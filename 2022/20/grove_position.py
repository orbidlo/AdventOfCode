# https://adventofcode.com/2022/day/20

from __future__ import annotations

from collections import deque
from pathlib import Path

import pytest

from libs import timeit, INPUT_FILE, INPUT_TEST, cmp

HERE = Path(__file__).parent.resolve()
POSITIONS = [1000, 2000, 3000]
DECRYPTION_KEY = 811589153


@timeit
def parse(input_file: Path) -> list[int]:
    data = input_file.read_text().splitlines()
    return list(int(number) for number in data)


# part 1
@timeit
def get_grove_coordinates_old(data: list[int], decryption_key: int = 1, times: int = 1) -> list[int]:
    """
        Original solution that is operating on array of indexes of original data.
        Changing the value in index list represents moving the original element to different position.
        Inefficiency is in having to change the position for all indexes in old_idx...new_idx
    """
    data = [num * decryption_key for num in data]
    wrap = len(data)
    indexes = list(range(wrap))
    for _ in range(times):
        for idx in range(wrap):
            old_idx = indexes[idx]
            # calculate new position by adding the original value (wrapped around)
            new_idx = (old_idx + data[idx]) % (wrap - 1)
            if new_idx == old_idx:
                continue
            # fix all indexes that are shifted
            idx_cmp = cmp(old_idx, new_idx)
            changed_indexes = range(new_idx, old_idx, idx_cmp)
            num_changes = len(changed_indexes)
            processed = 0
            for x, num in enumerate(indexes):
                if num in changed_indexes:
                    indexes[x] += idx_cmp
                    processed += 1
                    if processed == num_changes:
                        break
            # change index to new position
            indexes[idx] = new_idx
    # shuffle original list according to new ordering
    new_order = [y for x, y in sorted(zip(indexes, data))]
    zero_idx = new_order.index(0)

    return [new_order[(indexes[zero_idx] + pos) % wrap] for pos in POSITIONS]


@timeit
def get_grove_coordinates(data: list[int], decryption_key: int = 1, times: int = 1) -> list[int]:
    """
        More (4x) efficient and elegant implementation using deque. Instead of moving element by
        its value, remove the element, shift the rest opposite way using rotate, and reinsert.
    """
    # avoid duplicated values by adding index and convert to deque
    position_list = deque([(decryption_key * value, index) for index, value in enumerate(data)])
    for _ in range(times):
        for i, num in enumerate(data):
            num = decryption_key * num
            current_index = position_list.index((num, i))
            position_list.remove((num, i))
            position_list.rotate(-num)
            position_list.insert(current_index, (num, i))
    final_list = list(map(lambda x: x[0], position_list))
    zero_index = final_list.index(0)
    return [final_list[(zero_index + pos) % len(data)] for pos in POSITIONS]


@pytest.mark.parametrize(
    "key,times,expected", [
        (1, 1, 3),
        (DECRYPTION_KEY, 10, 1623178306)
    ])
def test_get_grove_coordinates(key, times, expected):
    input_file = HERE / INPUT_TEST
    data = parse(input_file)
    coords = get_grove_coordinates(data, key, times)
    assert sum(coords) == expected


def main():
    input_file = HERE / INPUT_FILE
    data = parse(input_file)
    coords = get_grove_coordinates(data, 1, 1)
    print(f'Sum of grove coordinates is:  {sum(coords)}')
    decrypted_coords = get_grove_coordinates(data=data, decryption_key=DECRYPTION_KEY, times=10)
    print(f'Sum of decrypted grove coordinates is:  {sum(decrypted_coords)}')


if __name__ == "__main__":
    main()
