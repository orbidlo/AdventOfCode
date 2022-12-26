# https://adventofcode.com/2022/day/22

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field
from enum import IntEnum
from itertools import zip_longest
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, Range, Point

HERE = Path(__file__).parent.resolve()
TEST_SIZE = 4
SIZE = 50

# RDLU
TEST_LINKS = [
    ['6R', '4U', '3U', '2U'], ['3L', '5D', '6D', '1U'], ['4L', '5L', '2R', '1L'],
    ['6U', '5U', '3R', '1D'], ['6L', '2D', '3D', '4D'], ['1R', '2L', '5R', '4R']
]
LINKS = [
    ['2L', '3U', '4L', '6L'], ['5R', '3R', '1R', '6D'], ['2D', '5U', '4U', '1D'],
    ['5L', '6U', '1L', '3L'], ['2R', '6R', '4R', '3D'], ['5D', '2U', '1U', '4D']
]


class Direction(IntEnum):
    R = 0
    D = 1
    L = 2
    U = 3

    def __add__(self, other: Direction) -> Direction:
        turn = [1, 0, -1, 0]
        return Direction((self._value_ + turn[other]) % 4)

    def opposite(self) -> Direction:
        return Direction((self._value_ + 2) % 4)

    def count_rotations(self, to: Direction) -> int:
        return (to - self) % 4


Link = tuple[int, Direction]
Instruction = int | Direction


@dataclass
class Side:
    idx: int
    size: int
    origin_top_left: Point
    links: list[Link] = field(default_factory=list)

    def create_links(self, links: list[str]) -> None:
        """ Create links to another Side and it's edge  """
        for num, d in links:
            self.links.append((int(num), Direction[d]))

    def has_point(self, point: Point) -> bool:
        conditions = [
            (self.origin_top_left.x <= point.x < (self.origin_top_left.x + self.size)),
            (self.origin_top_left.y <= point.y < (self.origin_top_left.y + self.size))
        ]
        return all(conditions)

    def on_edge(self, point: Point, direction: Direction) -> bool:
        if point.x == self.origin_top_left.x and direction == Direction.L:
            return True
        if point.x == (self.origin_top_left.x + self.size - 1) and direction == Direction.R:
            return True
        if point.y == self.origin_top_left.y and direction == Direction.U:
            return True
        if point.y == (self.origin_top_left.y + self.size - 1) and direction == Direction.D:
            return True
        return False

    def from_local(self, local_point: Point) -> Point:
        return local_point + self.origin_top_left

    def to_local(self, global_point: Point) -> Point:
        return global_point - self.origin_top_left


@dataclass
class InstructionList:
    raw: str  # 10R5L5R10L4R5L5

    def __post_init__(self):
        self.numbers = [int(n) for n in re.findall(r'\d+', self.raw)]
        self.directions = [Direction[d] for d in re.findall(r'[R,L]', self.raw)]

    def __iter__(self) -> Instruction:
        for pair in zip_longest(self.numbers, self.directions):
            yield from pair


@dataclass
class Grid:
    board: list[list[str]]
    _current_dir: Direction = Direction.R
    _current_pos: Point = field(init=False)
    _x_ranges: list[Range] = field(default_factory=list)
    _y_ranges: list[Range] = field(default_factory=list)
    sides: list[Side] = field(default_factory=list)

    def __repr__(self) -> str:
        return '\n'.join(''.join(b) for b in self.board)

    def __getitem__(self, point: Point) -> str:
        return self.board[point.y][point.x]

    def __setitem__(self, point, value):
        self.board[point.y][point.x] = value

    def __post_init__(self) -> None:
        self._current_pos = Point(self.get_row_range(0).min, 0)
        max_len = max(len(row) for row in self.board)
        for i, row in enumerate(self.board):
            self.board[i] += [' '] * (max_len - len(row))
        for x in range(0, len(self.board[0])):
            self._x_ranges.append(self.get_col_range(x))
        for y in range(0, len(self.board)):
            self._y_ranges.append(self.get_row_range(y))

    @property
    def current(self) -> tuple[Point, Direction]:
        return self._current_pos + 1, self._current_dir

    def do_move(self) -> None:
        def wrap(num: int, num_range: Range) -> int:
            pos = (num - num_range.min) % len(num_range)
            return num_range.min + pos

        translate = [Point(1, 0), Point(0, 1), Point(-1, 0), Point(0, -1)]
        x = self._current_pos.x
        y = self._current_pos.y
        new_pos = self._current_pos + translate[self._current_dir]
        wrapped = Point(wrap(new_pos.x, self._y_ranges[y]), wrap(new_pos.y, self._x_ranges[x]))
        if self.is_wall(wrapped):
            return
        self._current_pos = wrapped
        self[self._current_pos] = 'o'

    def do_3d_move(self) -> None:
        # RDLU
        translate = [Point(1, 0), Point(0, 1), Point(-1, 0), Point(0, -1)]

        def wrap(edge: Direction) -> Point:
            this_edge = self._current_dir
            this_point = this_side.to_local(self._current_pos)
            rotation_destination = edge.opposite()
            rotation_count = this_edge.count_rotations(rotation_destination)
            next_point = (this_point + translate[this_edge]) % this_side.size
            rotated_point = next_point
            for _ in range(rotation_count):
                rotated_point = rotated_point.rotate_right(this_side.size)
            return rotated_point

        this_side = self.get_side(self._current_pos)

        if this_side.on_edge(self._current_pos, self._current_dir):
            other_id, other_edge = this_side.links[self._current_dir]
            other_side = self.sides[other_id - 1]
            wrapped = other_side.from_local(wrap(other_edge))
            new_dir = other_edge.opposite()
        else:
            wrapped = self._current_pos + translate[self._current_dir]
            new_dir = self._current_dir
        if self.is_wall(wrapped):
            return
        self._current_pos = wrapped
        self._current_dir = new_dir
        self[self._current_pos] = 'o'

    def is_wall(self, point: Point) -> bool:
        return self[point] == '#'

    def do_instruction(self, instruction: Instruction) -> None:
        if isinstance(instruction, Direction):
            self._current_dir += instruction
            return
        while instruction:
            self.do_move()
            instruction -= 1

    def get_row_range(self, y: int) -> Range:
        row = ''.join(self.board[y])
        minimum = min(val for val in [row.find('.'), row.find('#')] if val >= 0)
        maximum = max(row.rfind('.'), row.rfind('#'))
        return Range(minimum, maximum)

    def get_col_range(self, x: int) -> Range:
        column = ''.join(row[x] for row in self.board)
        minimum = min(val for val in [column.find('.'), column.find('#')] if val >= 0)
        maximum = max(column.rfind('.'), column.rfind('#'))
        return Range(minimum, maximum)

    def construct_sides(self, size: int, links: list[list[str]]) -> None:
        self.sides = []
        counter = 1
        for y in range(0, len(self.board), size):
            for x in range(0, len(self.board[0]), size):
                point = Point(x, y)
                if self[point] != ' ':
                    side = Side(counter, size, Point(x, y))
                    side.create_links(links[counter - 1])
                    self.sides.append(side)
                    counter += 1

    def do_3d_instruction(self, instruction: Instruction) -> None:
        if isinstance(instruction, Direction):
            self._current_dir += instruction
            return
        while instruction:
            self.do_3d_move()
            instruction -= 1

    def get_side(self, point: Point) -> Side:
        for side in self.sides:
            if side.has_point(point):
                return side


@timeit
def parse(input_file: Path) -> tuple[Grid, InstructionList]:
    data = input_file.read_text().splitlines()
    instructions = InstructionList(data[-1])
    grid = Grid([list(line) for line in data[:-2]])
    return grid, instructions


# part 1
@timeit
def get_final_password(grid: Grid, instructions: InstructionList) -> int:
    for instruction in instructions:
        grid.do_instruction(instruction)
    (col, row), facing = grid.current
    return 1000 * row + 4 * col + facing


def test_get_final_password():
    input_file = HERE / INPUT_TEST
    grid, instructions = parse(input_file)
    answer = get_final_password(grid, instructions)
    print(grid)
    assert answer == 6032


# Part 2
@timeit
def get_3d_password(grid: Grid, instructions: InstructionList, size: int, links: list[list[str]]) -> int:
    grid.construct_sides(size, links)
    for instruction in instructions:
        grid.do_3d_instruction(instruction)
    (col, row), facing = grid.current
    return 1000 * row + 4 * col + facing


def test_get_3d_password():
    input_file = HERE / INPUT_TEST
    grid, instructions = parse(input_file)
    answer = get_3d_password(grid, instructions, TEST_SIZE, TEST_LINKS)
    # print(grid)
    assert answer == 5031


def main():
    input_file = HERE / INPUT_FILE
    grid, instructions = parse(input_file)
    answer = get_final_password(deepcopy(grid), instructions)
    print(f'Final password is: {answer}')

    answer_3d = get_3d_password(grid, instructions, SIZE, LINKS)
    print(f'Final password to 3d cube is: {answer_3d}')


if __name__ == "__main__":
    main()
