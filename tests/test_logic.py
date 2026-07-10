import random

import pytest
from logic import to_number, calc_tiered_payment, commas_to_dots

@pytest.mark.parametrize(
    'value, expected',
    [
        pytest.param('5|0|7.3|-5.7|inf|7', ['5', '0', '7.3', '-5.7', 'inf', '7'], id='str-with-sep'),
        pytest.param('5', 5.0, id='positive-int'),
        pytest.param('-5', -5.0, id='negative-int'),
        pytest.param('5.25', 5.25, id='float'),
        pytest.param('0', 0.0, id='ziro'),
        pytest.param('', 0, id='empty'),
        pytest.param(None, 0, id='none')
    ],
)

def test_to_num(value, expected):
    assert to_number(value) == expected

def test_to_number_rejects_non_numeric_string():
    with pytest.raises(ValueError):
        to_number('hau')

def test_with_random_num():
    seed_v = random.Random(54)

    for _ in range(100):
        number = str(seed_v.uniform(-50, 50))
        assert to_number(number) == float(number)