import pandas as pd

from pakkenellik.ssb import (
    add_municipality_population,
    add_rank,
    add_rate,
    get_county_population,
    get_municipality_population,
    population,
)


def _jsonstat_response() -> dict[str, object]:
    return {
        "id": ["Region", "ContentsCode", "Tid"],
        "size": [2, 1, 2],
        "dimension": {
            "Region": {
                "category": {
                    "index": {"0301": 0, "4636": 1},
                    "label": {"0301": "Oslo", "4636": "Solund"},
                }
            },
            "ContentsCode": {
                "category": {
                    "index": {"Folkemengde": 0},
                    "label": {"Folkemengde": "Befolkning per 1.1. (personer)"},
                }
            },
            "Tid": {
                "category": {
                    "index": {"2025": 0, "2026": 1},
                    "label": {"2025": "2025", "2026": "2026"},
                }
            },
        },
        "value": [724290, 728714, 740, 742],
    }


def _current_municipalities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "kommunenummer": "0301",
                "kommunenavn": "Oslo",
                "fylkesnummer": "03",
                "fylkesnavn": "Oslo",
                "siste_endret": "1925",
            },
            {
                "kommunenummer": "4636",
                "kommunenavn": "Solund",
                "fylkesnummer": "46",
                "fylkesnavn": "Vestland",
                "siste_endret": "2020",
            },
        ]
    )


def test_get_municipality_population_parses_ssb_jsonstat(monkeypatch) -> None:
    monkeypatch.setattr(
        population, "_post_statbank_query", lambda *args, **kw: _jsonstat_response()
    )
    monkeypatch.setattr(
        population, "load_current_municipalities", _current_municipalities
    )

    result = get_municipality_population(
        years=[2025, 2026],
        municipality_ids=["0301", "4636"],
    )

    solund_2026 = result.loc[
        (result["kommunenummer"] == "4636") & (result["år"] == "2026"), :
    ].iloc[0]
    assert solund_2026["folketall"] == 742
    assert solund_2026["kommunenavn"] == "Solund"
    assert solund_2026["fylkesnavn"] == "Vestland"


def test_get_county_population_uses_county_column(monkeypatch) -> None:
    monkeypatch.setattr(
        population, "_post_statbank_query", lambda *args, **kw: _jsonstat_response()
    )

    result = get_county_population(years=[2025, 2026], county_ids=["03", "46"])

    assert list(result.columns) == ["fylkesnummer", "år", "folketall"]
    assert result.iloc[0]["fylkesnummer"] == "0301"


def test_add_municipality_population_joins_on_code_and_year(monkeypatch) -> None:
    monkeypatch.setattr(
        population, "_post_statbank_query", lambda *args, **kw: _jsonstat_response()
    )
    df = pd.DataFrame(
        {
            "kommune": [301, 4636],
            "år": [2025, 2026],
            "hendelser": [10, 4],
        }
    )

    result = add_municipality_population(
        df,
        municipality_col="kommune",
        population_col="befolkning",
    )

    assert result.iloc[0]["befolkning"] == 724290
    assert result.iloc[1]["befolkning"] == 742


def test_add_rate_adds_rate_column() -> None:
    df = pd.DataFrame({"hendelser": [5], "folketall": [1000]})

    result = add_rate(df, numerator_col="hendelser", per=1000)

    assert result.iloc[0]["hendelser_per_1000"] == 5


def test_add_rank_can_rank_within_year() -> None:
    df = pd.DataFrame(
        {
            "år": [2025, 2025, 2026],
            "kommune": ["A", "B", "A"],
            "rate": [2.5, 7.5, 1.0],
        }
    )

    result = add_rank(df, value_col="rate", group_col="år", ascending=False)

    assert list(result["rank"]) == [2, 1, 1]
