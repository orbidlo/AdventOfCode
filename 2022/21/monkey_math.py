# https://adventofcode.com/2022/day/21

from __future__ import annotations

import operator
import typing
from copy import deepcopy
from pathlib import Path

from libs import timeit, INPUT_FILE, INPUT_TEST, to_int

HERE = Path(__file__).parent.resolve()

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

INV_OPS = {
    operator.add: operator.sub,
    operator.sub: operator.add,
    operator.mul: operator.truediv,
    operator.truediv: operator.mul
}

Expr = int | str
Op = typing.Callable[[int, int], int]


def invert_expression(parent: Expr, op: Op, left: Expr, right: Expr, get_left: bool = True) -> tuple[Op, Expr, Expr]:
    """
        Inverts expression `parent = op(left, right)` and returns expression to solve left or right side
        -> `left = inv_op(parent, right)`
        -> `right = inv_op(parent, left)` with handling of the special case for subtraction and division
        so e.g. `c=a-b` -> `a=c+b` & `b=a-c`, `c=a/b` -> `a=c*b` & `b=a/c`
    """
    if get_left:
        return INV_OPS[op], parent, right
    # get right
    if op == operator.sub or op == operator.truediv or op == operator.floordiv:
        return op, left, parent
    return INV_OPS[op], parent, left


class MonkeyDict(typing.Dict):
    def get_val(self, key: str) -> Expr:
        """ Recursive computation of given expression """
        if isinstance(self[key], int):
            return self[key]
        op, left, right = self[key]
        result = op(self.get_val(left), self.get_val(right))
        return result

    def has_human_input(self, key: str) -> bool:
        """ Recursive search of both subtrees if they contain human value. """
        if key == 'humn':
            return True
        if isinstance(self[key], int):
            return False
        op, left, right = self[key]
        return self.has_human_input(left) or self.has_human_input(right)

    def re_root_subtree(self, parent: str, new_root: str) -> None:
        """
            Re-roots tree of expressions from root to new root by finding the subtree containing new root
            and then creating inverse expression to calculate it from parent and the other subtree.
        """
        op, left, right = self[parent]
        left_subtree_has_human = self.has_human_input(left)
        right_subtree_has_human = self.has_human_input(right)
        if left_subtree_has_human and not right_subtree_has_human:
            if parent == 'root':
                # we are at current root, set left == right and re-root the subtree that contains new root
                self[parent] = operator.eq, left, right
                self.re_root_subtree(left, new_root)
                self[left] = self[right]
            elif left != new_root:
                # recursively re-root subtree and add expression to compute left
                self.re_root_subtree(left, new_root)
                self[left] = invert_expression(parent, op, left, right, get_left=True)
            else:
                # we reached new root, just add inverted operation
                self[left] = invert_expression(parent, op, left, right, get_left=True)
        elif right_subtree_has_human and not left_subtree_has_human:
            if parent == 'root':
                # we are at current root, set left == right and re-root the subtree that contains new root
                self[parent] = operator.eq, left, right
                self.re_root_subtree(right, new_root)
                self[right] = self[left]
            elif right != new_root:
                # recursively re-root subtree and add expression to compute right
                self.re_root_subtree(right, new_root)
                self[right] = invert_expression(parent, op, left, right, get_left=False)
            else:
                # we reached new root, just add inverted operation
                self[right] = invert_expression(parent, op, left, right, get_left=False)
        else:
            raise NotImplementedError


@timeit
def parse(input_file: Path) -> MonkeyDict[str, Expr]:
    monkeys = MonkeyDict()
    data = input_file.read_text().splitlines()
    for line in data:
        name, expr = line.split(': ')
        expr = to_int(expr)
        if isinstance(expr, str):
            left, op, right = expr.split()
            monkeys[name] = (OPS[op], left, right)
        else:
            monkeys[name] = expr
    return monkeys


# part 1
@timeit
def compute_root_monkey(monkeys: MonkeyDict[str, Expr]) -> int:
    return monkeys.get_val('root')


def test_compute_root_monkey():
    input_file = HERE / INPUT_TEST
    monkeys = parse(input_file)
    answer = compute_root_monkey(monkeys)
    assert answer == 152


# Part 2
@timeit
def get_human_number(monkeys: MonkeyDict[str, Expr]) -> int:
    new_root = 'humn'
    monkeys.re_root_subtree('root', new_root)
    return monkeys.get_val(new_root)


def test_get_human_number():
    input_file = HERE / INPUT_TEST
    monkeys = parse(input_file)
    answer = get_human_number(monkeys)
    assert answer == 301
    op, left, right = monkeys['root']
    assert monkeys.get_val(left) == 150 and monkeys.get_val(right) == 150


def main():
    input_file = HERE / INPUT_FILE
    monkeys = parse(input_file)
    root_answer = compute_root_monkey(deepcopy(monkeys))
    print(f'Root monkey yells: {root_answer:.0f}')

    human_answer = get_human_number(deepcopy(monkeys))
    print(f'Human should yell so root is equal: {human_answer:.0f}')


if __name__ == "__main__":
    main()
