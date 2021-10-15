from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import islice

import pytest

from future_map import FutureMap, future_map


@pytest.fixture(name="executor")
def fixture_executor():
    return ThreadPoolExecutor(max_workers=1)


def double(value):
    return value * 2


def test_future_map(executor):
    with executor:
        double_future = partial(executor.submit, double)
        results = list(FutureMap(double_future, range(4), 2))
        assert sorted(results) == [0, 2, 4, 6]


def test_future_map_function(executor):
    with executor:
        double_future = partial(executor.submit, double)
        results = list(future_map(double_future, range(4), 2))
        assert sorted(results) == [0, 2, 4, 6]


def test_future_with_infinite_iterable(executor):
    with executor:

        def inf_input():
            cnt = 0
            while True:
                yield cnt
                cnt += 1

        double_future = partial(executor.submit, double)
        results = list(islice(FutureMap(double_future, inf_input(), 2), 4))
        assert len(results) == 4


def test_future_with_error(executor):
    with executor:

        def raise_error(_):
            raise Exception("for test")

        error_future = partial(executor.submit, raise_error)
        with pytest.raises(Exception) as excinfo:
            list(FutureMap(error_future, range(4), 2))
        assert str(excinfo.value) == "for test"
