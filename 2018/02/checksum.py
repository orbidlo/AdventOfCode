# https://adventofcode.com/2018/day/2

from collections import Counter
from itertools import chain
import os.path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'
INPUT_TEST2 = 'input_test2.txt'


def get_id_list(input_file):
    with open(input_file) as f:
        id_list = f.read().splitlines()
    return id_list


def get_counts(word, number_of_duplicates):
    """
    Gives total number of duplicated letters within word
    """
    counts = Counter(chain.from_iterable(word))
    duplicates = Counter(counts.values())
    return duplicates[number_of_duplicates]


# part 1
def get_hash(input_file):
    pairs = []
    triplets = []
    for box_id in get_id_list(input_file):
        pairs.append(1 if get_counts(box_id, 2) > 0 else 0)
        triplets.append(1 if get_counts(box_id, 3) > 0 else 0)
    return sum(pairs) * sum(triplets)


def test_get_hash():
    result = get_hash(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert result == 12


# part 2
def get_common_letters(input_file):
    id_list = sorted(get_id_list(input_file))

    for pair in zip(id_list[:-1], id_list[1:]):
        common_letters = ''.join([l1 for l1, l2 in zip(*pair) if l1 == l2])
        if len(common_letters) == len(pair[0]) - 1:
            return common_letters
    return None


def test_get_common_letters():
    result = get_common_letters(os.path.join(os.path.dirname(__file__), INPUT_TEST2))
    assert result == 'fgij'


if __name__ == "__main__":
    print(f'Checksum for ids is {get_hash(INPUT_FILE)}')
    print(f'Common letters between two words are {get_common_letters(INPUT_FILE)}')
