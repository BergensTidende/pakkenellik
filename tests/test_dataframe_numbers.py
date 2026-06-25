import pandas as pd

from pakkenellik.dataframe.numbers import format_number, format_number_column, is_number


def test_is_number_accepts_numeric_strings_and_rejects_text() -> None:
    assert is_number("123.4")
    assert not is_number("abc")


def test_format_number_uses_norwegian_separators() -> None:
    assert format_number(1234567.89) == "1.234.567,89"
    assert format_number(-12345) == "-12.345"


def test_format_number_column_adds_formatted_column() -> None:
    df = pd.DataFrame({"value": [12345]})

    result = format_number_column(df, "value")

    assert result.loc[0, "value__fmt"] == "12.345"
