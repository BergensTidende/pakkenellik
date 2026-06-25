import pandas as pd

from pakkenellik.dataframe.datetime import add_hms, add_week_number, add_ymd


def test_add_ymd_and_hms_adds_datetime_parts() -> None:
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-02 03:04:05"])})

    result = add_hms(add_ymd(df, "date"), "date")

    assert result.loc[0, "year"] == 2024
    assert result.loc[0, "month"] == 1
    assert result.loc[0, "day"] == 2
    assert result.loc[0, "hour"] == 3
    assert result.loc[0, "minute"] == 4
    assert result.loc[0, "second"] == 5


def test_add_week_number_uses_iso_week() -> None:
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"])})

    result = add_week_number(df, "date")

    assert result.loc[0, "week_number"] == 1
