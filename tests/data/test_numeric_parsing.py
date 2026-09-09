from decimal import Decimal

import pytest

from database.seeds.transform_raw_to_staging import parse_decimal, parse_integer


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
@pytest.mark.parametrize("parser", [parse_decimal, parse_integer])
def test_non_finite_input_is_reported_as_bad_data_without_crashing(parser, value):
    errors = []
    assert parser(value, "test_field", errors, minimum=0) is None
    assert len(errors) == 1
    assert errors[0]["field"] == "test_field"


def test_finite_numeric_values_still_parse():
    errors = []
    assert parse_decimal("250 000,50 €", "prix", errors) == Decimal("250000.50")
    assert parse_integer("3", "pieces", errors) == 3
    assert not errors
