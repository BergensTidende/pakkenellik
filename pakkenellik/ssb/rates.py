# mypy: disable-error-code=no-any-unimported
from typing import Optional

import pandas as pd


def add_rate(
    df: pd.DataFrame,
    *,
    numerator_col: str,
    denominator_col: str = "folketall",
    per: int = 1000,
    output_col: Optional[str] = None,
) -> pd.DataFrame:
    """Add a rate column, for example incidents per 1,000 inhabitants."""
    result = df.copy()
    output = output_col or f"{numerator_col}_per_{per}"
    result[output] = result[numerator_col] / result[denominator_col] * per
    return result


def add_rank(
    df: pd.DataFrame,
    *,
    value_col: str,
    group_col: Optional[str] = None,
    ascending: bool = False,
    output_col: str = "rank",
    method: str = "min",
) -> pd.DataFrame:
    """Add rank for a value column, optionally within groups such as year."""
    result = df.copy()
    if group_col is None:
        result[output_col] = result[value_col].rank(
            ascending=ascending,
            method=method,
        )
    else:
        result[output_col] = result.groupby(group_col)[value_col].rank(
            ascending=ascending,
            method=method,
        )
    return result
