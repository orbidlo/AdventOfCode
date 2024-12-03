# https://adventofcode.com/2024/day/2

from __future__ import annotations
from pathlib import Path
from libs import timeit, INPUT_FILE, INPUT_TEST

HERE = Path(__file__).parent.resolve()
MAX_DIFFERENCE = 3
MIN_DIFFERENCE = 1


def parse_file(input_file: Path) -> list[str]:
    return input_file.read_text().splitlines()


class Report:
    def __init__(self, levels: list[int]):
        self.levels = levels

    @classmethod
    def parse(cls, report_str: str) -> Report:
        return cls([int(level) for level in report_str.split()])

    def is_decreasing(self) -> bool:
        return all(self.levels[i] > self.levels[i + 1] for i in range(len(self.levels) - 1))

    def is_increasing(self) -> bool:
        return all(self.levels[i] < self.levels[i + 1] for i in range(len(self.levels) - 1))

    def has_small_differences(self) -> bool:
        for i in range(len(self.levels) - 1):
            difference = abs(self.levels[i] - self.levels[i + 1])
            similar = (difference >= MIN_DIFFERENCE) and (difference <= MAX_DIFFERENCE)
            if not similar:
                return False
        return True

    def is_safe(self) -> bool:
        return (self.is_decreasing() or self.is_increasing()) and self.has_small_differences()

    def remove_level(self, level: int) -> Report:
        return Report(self.levels[:level] + self.levels[level + 1:])


# part 1
@timeit
def count_safe_reports(reports: list[str]) -> int:
    return sum(Report.parse(report).is_safe() for report in reports)


def test_count_safe_reports():
    test_data = parse_file(HERE / INPUT_TEST)
    assert count_safe_reports(test_data) == 2

# part 2
@timeit
def count_safe_reports_dampened(reports: list[str]) -> int:
    """
    Count the number of safe reports, considering reports that are not safe
    but can be made safe by removing one level.
    """
    safe_reports = 0
    for report_str in reports:
        report = Report.parse(report_str)
        if report.is_safe():
            safe_reports += 1
            continue
        for level_index in range(len(report.levels)):
            modified_report = report.remove_level(level_index)
            if modified_report.is_safe():
                safe_reports += 1
                break
    return safe_reports

def test_test_count_safe_reports_dampened():
    test_data = parse_file(HERE / INPUT_TEST)
    assert count_safe_reports_dampened(test_data) == 4


if __name__ == "__main__":
    final_data = parse_file(HERE / INPUT_FILE)

    final_safe_reports = count_safe_reports(final_data)
    print(f"Number of safe reports: {final_safe_reports}")

    final_safe_reports_dampened = count_safe_reports_dampened(final_data)
    print(f"Number of safe reports dampened: {final_safe_reports_dampened}")
