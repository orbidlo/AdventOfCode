# https://adventofcode.com/2021/day/3

import os
import pandas as pd

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'

FIRST_ROW = 0
LAST_ROW = -1


def parse_lines(input_file):
    with open(input_file) as f:
        parsed_lines = []
        for line in f.readlines():
            parsed_lines.append([int(c) for c in line.rstrip()])
    return parsed_lines


def binary_list_to_int(binary_list):
    return int(''.join(str(x) for x in binary_list), 2)


# part 1
def get_rates(input_file):
    parsed = parse_lines(input_file)

    # old solution without pandas
    # transposed = [list(line) for line in zip(*parsed)]
    # gamma_list = [1 if sum(trans_line) > len(trans_line) / 2 else 0 for trans_line in transposed]

    # get most common values
    gamma_list = pd.DataFrame(parsed).mode().values[0].tolist()
    # reverse list for least common values
    epsilon_list = [1 if x == 0 else 0 for x in gamma_list]

    gamma = binary_list_to_int(gamma_list)
    epsilon = binary_list_to_int(epsilon_list)

    return gamma, epsilon


def test_get_rates():
    test_gamma, test_epsilon = get_rates(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_gamma == 22
    assert test_epsilon == 9


# part 2

def filter_in_col(df, col, most_common=True):
    if df.shape[0] == 1:
        # we are done with one row/number left
        return df

    # detect if both numbers are equally common
    is_equally_common = bool(df[col].value_counts().min() == df[col].value_counts().max())

    most_common_number = df[col].value_counts().index[FIRST_ROW]
    least_common_number = df[col].value_counts().index[LAST_ROW]

    if most_common:
        if is_equally_common:
            filtered_value = 1
        else:
            filtered_value = int(most_common_number)
    else:
        if is_equally_common:
            filtered_value = 0
        else:
            filtered_value = int(least_common_number)

    result_df = df.loc[df[col] == filtered_value]
    return result_df


def get_life_support_rating(input_file):
    parsed = parse_lines(input_file)

    parsed_df = pd.DataFrame(parsed)
    oxygen_df = parsed_df.copy()
    co2_df = parsed_df.copy()

    for col in range(parsed_df.shape[1]):
        oxygen_df = filter_in_col(oxygen_df, col, True)
        co2_df = filter_in_col(co2_df, col, False)

    oxygen_rate = binary_list_to_int(oxygen_df.values[0].tolist())
    co2_rate = binary_list_to_int(co2_df.values[0].tolist())

    return oxygen_rate, co2_rate


def test_get_life_support_rating():
    test_oxygen_rating, test_co2_rating = get_life_support_rating(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert test_oxygen_rating == 23
    assert test_co2_rating == 10


if __name__ == "__main__":
    final_gamma, final_epsilon = get_rates(INPUT_FILE)
    print(f'Calculated gamma is {final_gamma} and epsilon is {final_epsilon}.\n'
          f'Power consumption of submarine is {final_gamma*final_epsilon}')

    final_oxygen, final_co2 = get_life_support_rating(INPUT_FILE)
    print(f'Calculated oxygen rate is {final_oxygen} and co2 rate is {final_co2}.\n'
          f'Life support rating of submarine is {final_oxygen*final_co2}')
