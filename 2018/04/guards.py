# https://adventofcode.com/2018/day/4

import pandas as pd
import os.path

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def parse_input(input_file):
    df = pd.read_csv(input_file, header=None, names=['text'])
    # extract datetime and set as index
    df.index = pd.to_datetime(df.text.str.replace('1518', '2018').str.extract(r'\[([^\]]+)\]')[0])
    df = df.sort_index()
    # extract guard id and forward fill to all their actions
    df['guard_id'] = df.text.str.extract(r'Guard #(\d+) begins shift').ffill()
    # extract when they were asleep
    df['asleep'] = df.text.str.contains(r'falls asleep', na=False)
    df = df[['guard_id', 'asleep']]
    # resample to 1 minute
    df = df.resample('1Min').ffill()
    return df


def get_most_sleep_guard(input_file):
    records = parse_input(input_file)
    # calculate total time spent sleeping per guard and get guard id of max value
    guard = records.groupby('guard_id').sum()['asleep'].idxmax()
    records_filtered = records[records.guard_id == guard]
    # filter actions just for that guard and get top minute spend sleeping
    minute = records_filtered.groupby(records_filtered.index.minute).sum()['asleep'].idxmax()

    return int(guard), int(minute)


def test_get_most_sleep_guard():
    guard, minute = get_most_sleep_guard(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert guard == 10
    assert minute == 24


def get_guard_per_minutes(input_file):
    records = parse_input(input_file)
    # get max of which minutes was each guard typically asleep
    guard, minute = records.groupby(['guard_id', records.index.minute]).sum().idxmax().tolist()[0]

    return int(guard), int(minute)


def test_get_guard_per_minutes():
    guard, minute = get_guard_per_minutes(os.path.join(os.path.dirname(__file__), INPUT_TEST))
    assert guard == 99
    assert minute == 45


if __name__ == "__main__":
    most_asleep_guard, most_asleep_minute = get_most_sleep_guard(INPUT_FILE)
    print(f"Part 1: ID of most asleep guard is {most_asleep_guard} in {most_asleep_minute} minute. "
          f"Result is {most_asleep_guard * most_asleep_minute}")

    sleepy_guard, sleepy_minute = get_guard_per_minutes(INPUT_FILE)
    print(f"Part 2: Most frequently asleep minute is {sleepy_minute} "
          f"by {sleepy_guard} guard. "
          f"Result is {sleepy_guard * sleepy_minute}.")
