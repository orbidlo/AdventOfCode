# https://adventofcode.com/2022/day/19

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()

STEPS = 24
MORE_STEPS = 32
# optimistic estimate of bots generated if we could build the bot every minute
TRIANGULAR_SEQUENCE = [(t - 1) * t // 2 for t in range(MORE_STEPS + 1)]


class Robot(Enum):
    GEODE = 3
    OBSIDIAN = 2
    CLAY = 1
    ORE = 0


@dataclass(frozen=True)
class Resource:
    ore: int = 0
    clay: int = 0
    obs: int = 0
    geode: int = 0

    def __add__(self, other: Resource) -> Resource:
        return Resource(self.ore + other.ore, self.clay + other.clay, self.obs + other.obs, self.geode + other.geode)

    def __sub__(self, other: Resource) -> Resource:
        return Resource(self.ore - other.ore, self.clay - other.clay, self.obs - other.obs, self.geode - other.geode)

    def add(self, ore: int = 0, clay: int = 0, obs: int = 0, geode: int = 0) -> Resource:
        return Resource(self.ore + ore, self.clay + clay, self.obs + obs, self.geode + geode)

    def sub(self, ore: int = 0, clay: int = 0, obs: int = 0, geode: int = 0) -> Resource:
        assert self.ore >= ore and self.clay >= clay and self.obs >= obs and self.geode >= geode
        return Resource(self.ore - ore, self.clay - clay, self.obs - obs, self.geode - geode)


@dataclass
class Blueprint:
    blueprint_id: int
    ore_bot: Resource
    clay_bot: Resource
    obsidian_bot: Resource
    geode_bot: Resource
    max_ore_cost: int = field(init=False)
    total_geodes: int = 0

    def __post_init__(self) -> None:
        self.max_ore_cost = max(self.ore_bot.ore, self.clay_bot.ore, self.obsidian_bot.ore, self.geode_bot.ore)
        self.max_clay_cost = self.obsidian_bot.clay
        self.max_obs_ost = self.geode_bot.obs

    def dfs(self, time_remain: int, goal_bot: Robot, bots: Resource, available: Resource):
        # print(f'time:{STEPS - time_remain}, goal:{goal_bot}, \nbots: {bots}, avail: {available} ')
        pruning_conditions = [
            # we generate enough resources to build any robot, no reason building more bots
            (goal_bot == Robot.ORE and bots.ore >= self.max_ore_cost),
            (goal_bot == Robot.CLAY and bots.clay >= self.max_clay_cost),
            # don't build obsidian/geode bot if we don't have the prerequisite bots
            (goal_bot == Robot.OBSIDIAN and (bots.obs >= self.max_obs_ost or bots.clay == 0)),
            (goal_bot == Robot.GEODE and bots.obs == 0),
            # upper bound on the amount of geodes we can generate is lower than the best solution so far
            (available.geode + bots.geode * time_remain + TRIANGULAR_SEQUENCE[time_remain] <= self.total_geodes)
        ]
        if any(pruning_conditions):
            # print('\tpruning')
            return

        while time_remain:
            # build ore bot if we can and then branch out on goal bot for t-1
            if goal_bot == Robot.ORE and available.ore >= self.ore_bot.ore:
                branch_bots = bots.add(ore=1)
                branch_available = available + bots - self.ore_bot
                for branch_goal in Robot:
                    self.dfs(time_remain - 1, branch_goal, branch_bots, branch_available)
                return
            # build clay bot if we can and then branch out on goal bot for t-1
            elif goal_bot == Robot.CLAY and available.ore >= self.clay_bot.ore:
                branch_bots = bots.add(clay=1)
                branch_available = available + bots - self.clay_bot
                for branch_goal in Robot:
                    self.dfs(time_remain - 1, branch_goal, branch_bots, branch_available)
                return
            # build obsidian bot if we can and then branch out on goal bot for t-1
            elif goal_bot == Robot.OBSIDIAN and \
                    available.ore >= self.obsidian_bot.ore and available.clay >= self.obsidian_bot.clay:
                branch_bots = bots.add(obs=1)
                branch_available = available + bots - self.obsidian_bot
                for branch_goal in Robot:
                    self.dfs(time_remain - 1, branch_goal, branch_bots, branch_available)
                return
            # build geode bot if we can and then branch out on goal bot for t-1
            elif goal_bot == Robot.GEODE and \
                    available.ore >= self.geode_bot.ore and available.obs >= self.geode_bot.obs:
                branch_bots = bots.add(geode=1)
                branch_available = available + bots - self.geode_bot
                for branch_goal in Robot:
                    self.dfs(time_remain - 1, branch_goal, branch_bots, branch_available)
                return
            # don't build anything and just generate resources
            time_remain -= 1
            available += bots
            # print(f'\twaiting! time: {STEPS - time_remain} (avail: {available})')

        self.total_geodes = max(self.total_geodes, available.geode)
        # print(f'best geodes: {self.total_geodes}')


@timeit
def parse(input_file: Path) -> list[Blueprint]:
    data = input_file.read_text().splitlines()
    blueprints = []
    for line in data:
        numbers = list(map(int, re.findall(r'\d+', line)))
        blueprint = Blueprint(
            blueprint_id=numbers[0],
            ore_bot=Resource(ore=numbers[1]),
            clay_bot=Resource(ore=numbers[2]),
            obsidian_bot=Resource(ore=numbers[3], clay=numbers[4]),
            geode_bot=Resource(ore=numbers[5], obs=numbers[6])
        )
        blueprints.append(blueprint)
    return blueprints


# part 1
@timeit
def get_quality_level(blueprints: list[Blueprint], steps: int) -> int:
    quality = 0
    for blueprint in blueprints:
        for goal_bot in Robot:
            blueprint.dfs(steps, goal_bot, Resource(ore=1), Resource())
        quality += blueprint.total_geodes * blueprint.blueprint_id
    return quality


def test_get_surface_area():
    input_file = HERE / INPUT_TEST
    blueprints = parse(input_file)
    quality_level = get_quality_level(blueprints, STEPS)
    assert quality_level == 33


# part 2
@timeit
def get_max_geodes(blueprints: list[Blueprint], steps: int) -> int:
    quality = 1
    for blueprint in blueprints[:3]:
        for goal_bot in Robot:
            blueprint.dfs(steps, goal_bot, Resource(ore=1), Resource())
        quality *= blueprint.total_geodes
    return quality


def test_get_max_geodes():
    input_file = HERE / INPUT_TEST
    blueprints = parse(input_file)
    quality_level = get_max_geodes(blueprints, MORE_STEPS)
    assert quality_level == 56 * 62


def main():
    input_file = HERE / INPUT_FILE
    blueprints = parse(input_file)
    quality_level = get_quality_level(blueprints, STEPS)
    print(f'Sum of blueprints\' quality levels is:  {quality_level}')
    num_geodes = get_max_geodes(blueprints, MORE_STEPS)
    print(f'Product of first 3 blueprints\' max geodes is:  {num_geodes}')


if __name__ == "__main__":
    main()
