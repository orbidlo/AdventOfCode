# https://adventofcode.com/2023/day/1

from pathlib import Path
from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()
INPUT_TEST2 = "input_test2.txt"

# since numbers as words can overlap, make sure we always leave in first and last letter
# so order in which we translate to digit doesn't matter
NUMBERS_TRANSLATE = {
    "one": "o1e",
    "two": "t2o",
    "three": "t3e",
    "four": "f4r",
    "five": "f5e",
    "six": "s6x",
    "seven": "s7n",
    "eight": "e8t",
    "nine": "n9e",
}


def parse_file(input_file: Path) -> list[str]:
    return input_file.read_text().splitlines()


def parse_calibration(data: list[str], numbers_as_words: bool = False) -> list[int]:
    calibrations = []
    for line in data:
        if numbers_as_words:
            for key, val in NUMBERS_TRANSLATE.items():
                line = line.replace(key, val)
        numbers_in_line = list(int(char) for char in line if char.isdigit())
        calibrations.append(numbers_in_line[0] * 10 + numbers_in_line[-1])
    return calibrations


# part 1
@timeit
def get_calibration(data: list[str]) -> int:
    calibrations = parse_calibration(data)
    return sum(calibrations)


def test_get_calibration():
    test_data = parse_file(HERE / INPUT_TEST)
    test_calibrations = get_calibration(test_data)
    assert test_calibrations == 142


# part 2
@timeit
def get_complex_calibration(data: list[str]) -> int:
    calibrations = parse_calibration(data, numbers_as_words=True)
    return sum(calibrations)


def test_get_complex_calibration():
    test_data = parse_file(HERE / INPUT_TEST2)
    test_calibrations = get_complex_calibration(test_data)
    assert test_calibrations == 281


if __name__ == "__main__":
    final_data = parse_file(HERE / INPUT_FILE)

    final_calibrations = get_calibration(final_data)
    print(f"Sum of all calibrations is: {final_calibrations}")

    final_complex_calibrations = get_complex_calibration(final_data)
    print(f"Sum of all complex calibrations is: {final_complex_calibrations}")
