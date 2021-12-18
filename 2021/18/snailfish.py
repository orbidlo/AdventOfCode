# https://adventofcode.com/2021/day/18

from __future__ import annotations

import logging
import os
import sys
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import product
from math import floor, ceil
from operator import add
from timeit import default_timer as timer
from typing import Iterator

import pytest

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

VALUE_THRESHOLD = 10
NESTED_TREE_LIMIT = 4


@dataclass
class Tree:
    """
        Binary tree with in-order traversal (left to right) able to compute magnitude and add another tree.
        Each node is in fact another tree, leaf is defined as having value and no left or right sub-tree.
        Leave pair is such tree that had both children leaves.
    """
    level: int
    parent: Tree | None
    value: int | None
    left: Tree | None
    right: Tree | None

    def __repr__(self) -> str:
        if self.is_leaf():
            return f'{self.value}'
        return f'[{repr(self.left)}, {repr(self.right)}]'

    def __eq__(self, other: Tree) -> bool:
        return self.value == other.value and \
               self.level == other.level and \
               self.left == other.left and \
               self.right == other.right

    def __add__(self, other_tree: Tree) -> Tree:
        left = deepcopy(self)
        right = deepcopy(other_tree)
        tree = Tree(level=0, parent=None, value=None, left=left, right=right)
        left.re_root(tree)
        right.re_root(tree)
        tree.reduce()
        return tree

    @property
    def magnitude(self) -> int:
        if self.is_leaf():
            return self.value
        return 3 * self.left.magnitude + 2 * self.right.magnitude

    @classmethod
    def parse(cls, tree_def: list[list | int]) -> Tree:
        return cls.create_tree(parent=None, level=0, tree_def=tree_def)

    @classmethod
    def create_tree(cls, parent: Tree | None, level: int, tree_def: list | int) -> Tree:
        if isinstance(tree_def, int):
            return cls(level=level, parent=parent, value=tree_def, left=None, right=None)
        left, right = tree_def
        tree = cls(level=level, parent=parent, value=None, left=None, right=None)
        tree.left = cls.create_tree(parent=tree, level=level + 1, tree_def=left)
        tree.right = cls.create_tree(parent=tree, level=level + 1, tree_def=right)
        return tree

    def re_root(self, parent: Tree) -> None:
        """ Add another level above root tree and recalculate levels to reflect this.  """
        assert self.is_root()
        self.parent = parent
        self._add_level()

    def _add_level(self) -> None:
        self.level += 1
        if not self.is_leaf():
            self.left._add_level()
            self.right._add_level()

    def all_leaves(self) -> Iterator[Tree]:
        """ Generate all leaves in in-order traversal (left to right). """
        if self.is_leaf():
            yield self
        else:
            yield from self.left.all_leaves()
            yield from self.right.all_leaves()

    def all_leaf_pairs(self) -> Iterator[Tree]:
        """ Generate all leaf pairs in in-order traversal (left to right). """
        if self.is_leaf():
            return
        if self.is_leaf_pair():
            yield self
        else:
            yield from self.left.all_leaf_pairs()
            yield from self.right.all_leaf_pairs()

    def is_leaf(self) -> bool:
        return self.value is not None and self.left is None and self.right is None

    def is_leaf_pair(self) -> bool:
        return not self.is_leaf() and self.left.is_leaf() and self.right.is_leaf()

    def is_root(self) -> bool:
        return self.parent is None

    def get_root(self) -> Tree:
        if self.is_root():
            return self
        return self.parent.get_root()

    def is_left(self) -> bool:
        return not self.is_root() and self is self.parent.left

    def is_right(self) -> bool:
        return not self.is_root() and self is self.parent.right

    def get_deep_nested_pair(self, limit: int = NESTED_TREE_LIMIT) -> Tree | None:
        """ Get leftmost pair that is nested exactly NESTED_TREE_LIMIT deep. """
        for pair in self.all_leaf_pairs():
            if pair.level == limit:
                return pair
        return None

    def get_leaf_above_threshold(self, threshold: int = VALUE_THRESHOLD) -> Tree | None:
        """ Get leftmost leaf which has value larger or equal to VALUE_THRESHOLD """
        for leaf in self.all_leaves():
            if leaf.value >= threshold:
                return leaf
        return None

    def reduce(self) -> None:
        """ Reduce tree by one of actions in this order: Explode too deep nested pairs and split big leaves.  """
        while True:
            if deep_pair := self.get_deep_nested_pair():
                deep_pair.explode()
                continue
            if big_leaf := self.get_leaf_above_threshold():
                big_leaf.split()
                continue
            break

    def explode(self):
        """
            Transform current leaf pair:
                - add its left child value to the nearest left leaf
                - add its right child value to the nearest right leaf
                - transforming leaf pair to leaf and setting it's value to 0.
            This is done by using our implementation of in-order traversal to generate all leaves.

        """
        assert self.is_leaf_pair()
        # remember previous leaf to be able to access it once we get to the left child
        prev_leaf = None
        for leaf in self.get_root().all_leaves():
            if leaf is self.left:
                if prev_leaf:
                    prev_leaf.value += self.left.value
            # here check that prev_leaf is our right child to be able to easily access next node to the right as leaf
            elif prev_leaf is self.right:
                leaf.value += self.right.value
                break
            prev_leaf = leaf
        # once we are done exploding values to the left and to the right, reset tree to be a leaf with zero value
        self.left = None
        self.right = None
        self.value = 0
        assert self.is_leaf()

    def split(self):
        """ Split current leaf into leaf pair such that their value add to the original value. """
        assert self.is_leaf()
        self.left = self.create_tree(parent=self, level=self.level + 1, tree_def=floor(self.value / 2))
        self.right = self.create_tree(parent=self, level=self.level + 1, tree_def=ceil(self.value / 2))
        self.value = None
        assert self.is_leaf_pair()


def parse_file(input_file: str) -> list[Tree]:
    """ Parse given file into list of Trees. """
    parsed_trees = []
    with open(input_file) as f:
        for line in f:
            tree_def = eval(line.strip())
            parsed_trees.append(Tree.parse(tree_def))
    return parsed_trees


# part 1
def calculate_sum(trees: list[Tree]) -> Tree:
    """ Calculate cumulative sum to all members of list of Trees.  """
    return reduce(add, trees)


def test_calculate_sum():
    trees = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_tree = calculate_sum(trees)
    assert test_tree.magnitude == 4140


# part 2
def find_largest_magnitude(trees: list[Tree]) -> Tree:
    """
        Find the largest magnitude we can get by adding two Trees from the parsed list, where A+B != B+A.
        To generate all pairs cartesian product (from itertools) is used, only filtering out double identical trees.
    """
    tree_pairs = product(trees, trees)
    return max((left + right).magnitude for left, right in tree_pairs if left is not right)


def test_find_largest_magnitude():
    trees = parse_file(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    test_magnitude = find_largest_magnitude(trees)

    assert test_magnitude == 3993


def test_addition():
    assert (Tree.parse([[[[4, 3], 4], 4], [7, [[8, 4], 9]]]) + Tree.parse([1, 1])) == \
           Tree.parse([[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]])


def test_split():
    tree = Tree.parse([[[[0, 7], 4], [15, [0, 13]]], [1, 1]])
    tree.get_leaf_above_threshold().split()
    assert tree == Tree.parse([[[[0, 7], 4], [[7, 8], [0, 13]]], [1, 1]])


@pytest.mark.parametrize(
    "tree_def,expected", [
        ([[[[[9, 8], 1], 2], 3], 4], [[[[0, 9], 2], 3], 4]),
        ([7, [6, [5, [4, [3, 2]]]]], [7, [6, [5, [7, 0]]]]),
        ([[6, [5, [4, [3, 2]]]], 1], [[6, [5, [7, 0]]], 3]),
        ([[3, [2, [1, [7, 3]]]], [6, [5, [4, [3, 2]]]]], [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]]),
        ([[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]], [[3, [2, [8, 0]]], [9, [5, [7, 0]]]])
    ])
def test_explode(tree_def, expected):
    tree = Tree.parse(tree_def)
    tree.get_deep_nested_pair().explode()
    assert tree == Tree.parse(expected)


@pytest.mark.parametrize(
    "tree_def,expected", [
        ([9, 1], 29),
        ([[9, 1], [1, 9]], 129),
        ([[1, 2], [[3, 4], 5]], 143),
        ([[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]], 1384),
        ([[[[1, 1], [2, 2]], [3, 3]], [4, 4]], 445),
        ([[[[3, 0], [5, 3]], [4, 4]], [5, 5]], 791),
        ([[[[5, 0], [7, 4]], [5, 5]], [6, 6]], 1137),
        ([[[[8, 7], [7, 7]], [[8, 6], [7, 7]]], [[[0, 7], [6, 6]], [8, 7]]], 3488)
    ])
def test_tree_magnitude(tree_def, expected):
    tree = Tree.parse(tree_def)
    assert tree.magnitude == expected


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    final_tree = calculate_sum(parse_file(INPUT_FILE))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Final magnitude after adding all trees is {final_tree.magnitude}.')

    start_time = timer()
    final_magnitude = find_largest_magnitude(parse_file(INPUT_FILE))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Largest magnitude after adding two of given trees is {final_magnitude}.')
