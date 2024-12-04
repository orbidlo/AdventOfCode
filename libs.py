from __future__ import annotations

import functools
import time
import weakref
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from itertools import product
from typing import Iterator, Any, NamedTuple, Callable

INPUT_FILE = "input.txt"
INPUT_TEST = "input_test.txt"


def to_int(num: str) -> str | int:
    try:
        return int(num)
    except ValueError:
        return num


def timeit(count: int | Callable = 1):
    if callable(count):
        actual_count = 1
    else:
        actual_count = count
    if actual_count < 1:
        raise ValueError("Count must be at least 1!")
    def decorator(func):
        @wraps(func)
        def timeit_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            for i in range(actual_count):
                result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            time_per_call = total_time / actual_count
            print(f"\tFunction {func.__name__} took {time_per_call * 1000:.2f} ms")
            return result
        return timeit_wrapper
    return decorator(count) if callable(count) else decorator


def lru_cache(maxsize=128, typed=False):
    """LRU cache usable for class methods."""

    def decorator(my_func):
        @functools.wraps(my_func)
        def wrapped_func(self, *args, **kwargs):
            self_weak = weakref.ref(self)

            @functools.wraps(my_func)
            @functools.lru_cache(maxsize=maxsize, typed=typed)
            def cached_method(*my_args, **my_kwargs):
                return my_func(self_weak(), *my_args, **my_kwargs)

            setattr(self, my_func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    if callable(maxsize) and isinstance(typed, bool):
        # The user_function was passed in directly via the maxsize argument
        func, maxsize = maxsize, 128
        return decorator(func)

    return decorator


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def cmp(a: int, b: int) -> int:
    # -1 when a<b, 0 when a==b, 1 when a>b
    return (a > b) - (a < b)


class Point(NamedTuple):
    x: int
    y: int

    def __iter__(self) -> int:
        yield self.x
        yield self.y

    def __lt__(self, other: Point) -> bool:
        if self.x < other.x:
            return True
        if self.x > other.x:
            return False
        if self.x == other.x:
            return self.y < other.y

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Any) -> Point:
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Point(self.x + other, self.y + other)
        raise NotImplementedError

    def __sub__(self, other: Any) -> Point:
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        if isinstance(other, int):
            return Point(self.x - other, self.y - other)
        raise NotImplementedError

    def __mul__(self, other: int) -> Point:
        return Point(self.x * other, self.y * other)

    def __mod__(self, other: int) -> Point:
        return Point(self.x % other, self.y % other)

    def get_manhattan_distance(self, point: Point) -> int:
        # sum of absolute difference between coordinates
        distance = 0
        for diff_1, diff_2 in zip(self, point):
            distance += abs(diff_1 - diff_2)
        return distance

    def rotate_right(self, size: int) -> Point:
        return Point(size - self.y - 1, self.x)


class Dirs(Enum):
    DOWN = Point(0, -1)
    UP = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)


@dataclass(frozen=True)
class Voxel:
    x: int
    y: int
    z: int

    def __add__(self, other: Voxel) -> Voxel:
        return Voxel(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iter__(self) -> int:
        yield self.x
        yield self.y
        yield self.z

    def is_adjacent(self, other: Voxel) -> bool:
        return self.get_manhattan_distance(other) == 1

    def get_manhattan_distance(self, other: Voxel) -> int:
        # sum of absolute difference between coordinates
        distance = 0
        for diff_1, diff_2 in zip(self, other):
            distance += abs(diff_1 - diff_2)
        return distance

    def get_neighbor(self) -> Voxel:
        for diff in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
            yield self + Voxel(*diff)


@dataclass(frozen=True)
class Range:
    """
    Class implementing distance from min to max (both included).
    Has ability to detect overlapping with another and to split by intersection.
    """

    min: int
    max: int

    def __post_init__(self):
        assert self.min <= self.max, "First parameter of range must be lower or equal to the second one."

    def __len__(self):
        """Length of range."""
        return self.max - self.min + 1

    def __eq__(self, other: Range) -> bool:
        return self.min == other.min and self.max == other.max

    def __lt__(self, other: Range) -> bool:
        if self.min < other.min:
            return True
        if other.min < self.min:
            return False
        if self.min == other.min:
            return self.max < other.max

    def __iter__(self) -> Iterator[int]:
        yield from range(self.min, self.max + 1)

    def __contains__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.min <= other <= self.max
        if isinstance(other, Range):
            if self == other:
                return True
            return other.min in self and other.max in self
        raise NotImplementedError

    def __add__(self, other: Any) -> Range:
        if isinstance(other, int):
            return Range(self.min + other, self.max + other)
        if isinstance(other, Range):
            assert self.overlaps(other) or self.adjacent(
                other
            ), "Cannot merge ranges that are not overlapping or adjacent."
            return Range(min(self.min, other.min), max(self.max, other.max))

    def overlaps(self, other: Range) -> bool:
        return self.max >= other.min and self.min <= other.max

    def adjacent(self, other: Range) -> bool:
        return other.min == self.max + 1 or self.min == other.max + 1

    def get_intersection(self, other: Range) -> Range | None:
        if self == other:
            return self
        new_range_min, new_range_max = max(self.min, other.min), min(self.max, other.max)
        if new_range_min > new_range_max:
            # no intersection
            return None
        return Range(new_range_min, new_range_max)

    def split(self, item: Any) -> list[Range]:
        """Split range by intersection with another range."""
        if isinstance(item, Range):
            if self == item:
                return [self]
            intersection = self.get_intersection(item)
            assert intersection is not None, "Cannot split range if it doesn't have intersection with the other."
            if self.min == intersection.min:
                return [intersection, Range(intersection.max + 1, self.max)]
            if self.max == intersection.max:
                return [Range(self.min, intersection.min - 1), intersection]
            # intersection is within self
            return [Range(self.min, intersection.min - 1), intersection, Range(intersection.max + 1, self.max)]
        raise NotImplementedError


class Cuboid(NamedTuple):
    x: Range
    y: Range
    z: Range

    def __len__(self):
        """Volume of cuboid."""
        return len(self.x) * len(self.y) * len(self.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, (Cuboid, Voxel)):
            return item.x in self.x and item.y in self.y and item.z in self.z
        raise NotImplementedError

    def overlaps(self, other: Cuboid) -> bool:
        if self == other:
            return True
        return all(axis.overlaps(other_axis) for axis, other_axis in zip(self, other))

    def get_intersection(self, other: Cuboid) -> Cuboid | None:
        if self == other:
            return self
        ranges = []
        for axis, other_axis in zip(self, other):
            axis_intersection = axis.get_intersection(other_axis)
            if axis_intersection is None:
                return None
            ranges.append(axis_intersection)
        return Cuboid(*ranges)

    def extract(self, other: Cuboid) -> set[Cuboid]:
        """Split self, extract intersection with another cuboid and return rest of sub-cuboids."""
        new_cuboids = set()
        if self == other:
            return set()
        intersection = self.get_intersection(other)
        assert intersection is not None, "Cannot split cuboid if it doesn't have intersection with the other."
        split_ranges = []
        for axis, other_axis in zip(self, intersection):
            split_ranges.append(axis.split(other_axis))
        for x, y, z in product(*split_ranges):
            new_cuboid = Cuboid(x, y, z)
            if new_cuboid != intersection:
                new_cuboids.add(new_cuboid)
        print(f"Splitting into {len(new_cuboids)} new cuboids." f"\nThrowing away {intersection}.")
        return new_cuboids
