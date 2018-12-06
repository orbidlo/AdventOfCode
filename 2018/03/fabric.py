# https://adventofcode.com/2018/day/3

import re
from collections import namedtuple
from itertools import combinations
import os.path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'
INPUT_REGEX = r'(?P<id>\d+) @ (?P<left>\d+),(?P<top>\d+): (?P<width>\d+)x(?P<height>\d+)'

Claim = namedtuple('Claim', 'id left top right bottom')
# inch is defined by it's left top with width and height 1
Inch = namedtuple('Inch', 'left top')


def parse_input(input_file):
    # get list of all defined claims
    parsed = set()
    pattern = re.compile(INPUT_REGEX)
    with open(input_file) as f:
        for line in f:
            result = pattern.search(line)
            if result:
                res_dict = result.groupdict()
                claim = Claim(
                    res_dict['id'],
                    int(res_dict['left']),
                    int(res_dict['top']),
                    int(res_dict['left']) + int(res_dict['width']),
                    int(res_dict['top']) + int(res_dict['height'])
                )
                parsed.add(claim)
    return parsed


def get_inches(claim):
    # returns all individual square inches that are contained within given claim
    inches = []
    for x in range(claim.left, claim.right):
        for y in range(claim.top, claim.bottom):
            inches.append(Inch(x, y))
    return inches


def get_overlap(a, b):  # returns None if claims don't intersect
    left_x = max(a.left, b.left)
    right_x = min(a.right, b.right)
    top_y = max(a.top, b.top)
    bottom_y = min(a.bottom, b.bottom)

    dx = right_x - left_x
    dy = bottom_y - top_y

    if (dx > 0) and (dy > 0):
        return Claim('overlap', left_x, top_y, left_x + dx, top_y + dy)


def get_all_inches(input_file):
    overlap_inches = set()  # set of all individual inches from overlap claims
    claims = parse_input(input_file)
    candidates = claims.copy()

    for (a, b) in combinations(claims, 2):
        overlap = get_overlap(a, b)
        if overlap:
            candidates.discard(a)
            candidates.discard(b)
            overlap_inches.update(get_inches(overlap))
    return len(overlap_inches), candidates.pop().id


def test_get_all_inches():
    all_inches, good_claims = get_all_inches(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert all_inches == 4
    assert good_claims == '3'


if __name__ == "__main__":
    all_inches, good_claims = get_all_inches(INPUT_FILE)

    print(f'There are {all_inches} square inches with at least two claims')
    print(f'Good claims are {good_claims}')
