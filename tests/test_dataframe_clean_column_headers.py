import pandas as pd

from pakkenellik.dataframe.clean_column_headers import (
    clean_column_header,
    clean_column_headers,
)


def test_clean_column_header_normalizes_common_norwegian_characters() -> None:
    assert (
        clean_column_header(
            "  Ærlig Økonomi-År! ", "_ abcdefghijklmnopqrstuvwxyz0123456789", [" ", "-"]
        )
        == "aerlig_okonomi_aar"
    )


def test_clean_column_headers_renames_dataframe_columns() -> None:
    df = pd.DataFrame({"Første kolonne": [1], "Andre-kolonne": [2]})

    result = clean_column_headers(df)

    assert list(result.columns) == ["forste_kolonne", "andre_kolonne"]
