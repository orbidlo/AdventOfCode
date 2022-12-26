# https://adventofcode.com/2022/day/18

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import cached_property
from operator import attrgetter
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, Range, Voxel

HERE = Path(__file__).parent.resolve()


@dataclass
class Grid:
    lava: set[Voxel]

    @cached_property
    def range(self) -> tuple[Range, Range, Range]:
        x_range = min(self.lava, key=attrgetter('x')).x, max(self.lava, key=attrgetter('x')).x + 1
        y_range = min(self.lava, key=attrgetter('y')).y, max(self.lava, key=attrgetter('y')).y + 1
        z_range = min(self.lava, key=attrgetter('z')).z, max(self.lava, key=attrgetter('z')).z + 1

        return Range(*x_range), Range(*y_range), Range(*z_range)

    def within_bounds(self, voxel: Voxel) -> bool:
        x_range, y_range, z_range = self.range
        # make sure  we look to one lower than minimum and one higher than maximum
        conditions = [
            (x_range.min - 1 <= voxel.x <= x_range.max),
            (y_range.min - 1 <= voxel.y <= y_range.max),
            (z_range.min - 1 <= voxel.z <= z_range.max)
        ]
        if all(conditions):
            return True
        return False


@timeit
def parse(input_file: Path) -> Grid:
    voxels = set()
    data = input_file.read_text().splitlines()
    for line in data:
        x, y, z = line.split(',')
        voxels.add(Voxel(int(x), int(y), int(z)))
    grid = Grid(lava=voxels)
    return grid


# part 1
@timeit
def get_surface_area(grid: Grid) -> int:
    surfaces = 0
    for voxel in grid.lava:
        surface = 6
        for neighbor in voxel.get_neighbor():
            if neighbor in grid.lava:
                surface -= 1
        surfaces += surface
    return surfaces


def test_get_surface_area():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    area = get_surface_area(grid)
    assert area == 64


# part 2
@timeit
def get_outer_surface_area(grid: Grid) -> int:
    touches_lava = 0
    x_range, y_range, z_range = grid.range
    # get voxel that is outside of our lava droplet
    voxel = Voxel(x_range.min, y_range.min, z_range.min)
    assert voxel not in grid.lava
    queue = deque([voxel])
    visited = {voxel}
    # do DFS search for all neighbors within our expanded bounds and if they are lava, can be touched by water
    while queue:
        current = queue.popleft()
        for neighbor in current.get_neighbor():
            if neighbor in grid.lava:
                touches_lava += 1
            elif neighbor not in visited and grid.within_bounds(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
    return touches_lava


def test_get_outer_surface_area():
    input_file = HERE / INPUT_TEST
    grid = parse(input_file)
    area = get_outer_surface_area(grid)
    assert area == 58


def main():
    input_file = HERE / INPUT_FILE
    grid = parse(input_file)
    area = get_surface_area(grid)
    print(f'Surface area of lava droplet is: {area}')

    outer_area = get_outer_surface_area(grid)
    print(f'Outer surface area of lava droplet is: {outer_area}')


if __name__ == "__main__":
    main()
