# https://adventofcode.com/2024/day/1

from collections import Counter
from pathlib import Path
from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()


def parse_location_ids(data: list[str]) -> tuple[list[int], list[int]]:
    """Split each line containing pair of integer values and transpose it into two lists"""
    list_of_pairs = [map(int, line.split()) for line in data]
    left_ids, right_ids = zip(*list_of_pairs) # transpose
    assert len(left_ids) == len(right_ids)
    return list(left_ids), list(right_ids)


def parse_file(input_file: Path) -> tuple[list[int], list[int]]:
    left_ids, right_ids = parse_location_ids(input_file.read_text().splitlines())
    return left_ids, right_ids


# part 1
@timeit
def get_distances(left_ids: list[int], right_ids: list[int]) -> int:
    distances = [abs(left - right) for left, right in zip(sorted(left_ids), sorted(right_ids))]
    return sum(distances)


def test_get_distances():
    test_distances = get_distances(*parse_file(HERE / INPUT_TEST))
    assert test_distances == 11


# part 2
@timeit
def get_similarity(left_ids: list[int], right_ids: list[int]) -> int:
    counts_right = Counter(right_ids)
    similarity = [left * counts_right[left] for left in left_ids]
    return sum(similarity)


def test_get_similarity():
    test_similarity = get_similarity(*parse_file(HERE / INPUT_TEST))
    assert test_similarity == 31


if __name__ == "__main__":
    final_ids_a, final_ids_b = parse_file(HERE / INPUT_FILE)

    final_distances = get_distances(final_ids_a, final_ids_b)
    print(f"Total distance between the locations: {final_distances}")

    final_similarity = get_similarity(final_ids_a, final_ids_b)
    print(f"Total similarity of the two location lists: {final_similarity}")
