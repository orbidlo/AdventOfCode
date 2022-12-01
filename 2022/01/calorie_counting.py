# https://adventofcode.com/2022/day/1


from pathlib import Path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

HERE = Path(__file__).parent.resolve()


def get_calories_sum(input_file: Path) -> list[int]:
    elf_sums = []
    for elf_calories in input_file.read_text().split(sep='\n\n'):
        elf_sums.append(sum(int(cal) for cal in elf_calories.splitlines()))
    return elf_sums


# part 1
def count_max_calories(input_file: Path) -> int:
    calories = get_calories_sum(input_file)
    return max(calories)


def test_count_max_calories():
    test_count = count_max_calories(HERE / INPUT_TEST)
    assert test_count == 24000


# part 2
def count_top_three_calories(input_file: Path) -> int:
    calories = get_calories_sum(input_file)
    return sum(calories.sort(reverse=True)[0:3])


def test_count_top_three_calories():
    test_count = count_top_three_calories(HERE / INPUT_TEST)
    assert test_count == 45000


if __name__ == "__main__":
    max_calories = count_max_calories(HERE / INPUT_FILE)
    print(f'The Elf with most calories has {max_calories} calories.')

    top_three_calories = count_top_three_calories(HERE / INPUT_FILE)
    print(f'Sum of all the calories from top three Elves is {top_three_calories}.')
