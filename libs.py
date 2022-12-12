import time
from functools import wraps

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        total_time = end_time - start_time
        print(f'\tFunction {func.__name__} took {total_time / 1000} μs')
        return result

    return timeit_wrapper


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def cmp(a: int, b: int) -> int:
    # -1 when a<b, 0 when a==b, 1 when a>b
    return (a > b) - (a < b)
