# https://adventofcode.com/2022/day/7

from __future__ import annotations

import time
import typing

from dataclasses import dataclass, field
from functools import wraps, cached_property
from pathlib import Path
from textwrap import indent

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()

SMALL_SIZE = 100000
DISK_SIZE = 70000000
TARGET_SIZE = 30000000


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


@dataclass
class File:
    name: str
    size: int

    def __repr__(self) -> str:
        return f'- {self.name} (file, size={self.size})\n'


@dataclass
class Directory:
    name: str
    parent: Directory | None = None
    children: typing.List[Directory | File] = field(default_factory=list)

    def __getitem__(self, name: str) -> Directory | File:
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(name)

    def __repr__(self) -> str:
        repr_str = f'- {self.name} (dir, size={self.size})\n'
        for child in self.children:
            repr_str += indent(f'{repr(child)}', '\t')
        return repr_str

    def __setitem__(self, name: str, node: Directory | File) -> None:
        if isinstance(node, Directory):
            node.parent = self
        self.children.append(node)

    @cached_property
    def size(self) -> int:
        size = 0
        for child in self.children:
            size += child.size
        return size

    def get_dir_sizes(self):
        for child in self.children:
            if isinstance(child, Directory):
                yield from child.get_dir_sizes()
        yield self.size


@timeit
def parse_input(input_file: Path) -> Directory:
    current = None
    root = Directory(name='/')
    with open(input_file) as file:
        for line in file:
            match line.strip().split():
                case ['$', 'ls']:
                    continue
                case ['$', 'cd', '/']:
                    current = root
                case ['$', 'cd', '..']:
                    current = current.parent
                case ['$', 'cd', name]:
                    current = current[name]
                case ['dir', name]:
                    current[name] = Directory(name=name)
                case [size, name]:
                    current[name] = File(name=name, size=int(size))
    return root


# part 1
@timeit
def sum_small_dirs(root: Directory) -> int:
    sizes = list(root.get_dir_sizes())
    return sum(size for size in sizes if size <= SMALL_SIZE)


def test_find_small_dirs():
    root = parse_input(HERE / INPUT_TEST)
    assert sum_small_dirs(root) == 95437


# part 2
@timeit
def find_smallest_dir_to_delete(root: Directory) -> int:
    sizes = list(root.get_dir_sizes())
    root_size = sizes[-1]
    must_delete = TARGET_SIZE - DISK_SIZE + root_size
    for size in sorted(sizes):
        if size > must_delete:
            return size


def test_find_smallest_dir_to_delete():
    root = parse_input(HERE / INPUT_TEST)
    assert find_smallest_dir_to_delete(root) == 24933642


def main():
    root = parse_input(HERE / INPUT_FILE)
    sum_size = sum_small_dirs(root)
    print(f'The sum of sizes of all small (<{SMALL_SIZE} size) directories is {sum_size}.')

    delete_size = find_smallest_dir_to_delete(root)
    print(f'The size of smallest directory to delete to clear enough space is: {delete_size}')


if __name__ == "__main__":
    main()
