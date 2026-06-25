# mypy: disable-error-code=no-any-unimported
from collections.abc import Iterable
from typing import Optional

import pandas as pd
import requests

from pakkenellik.regions import (
    add_municipality_info,
    load_current_municipalities,
    load_regions_history,
    normalize_county_id,
    normalize_municipality_id,
)

STATBANK_API_BASE_URL = "https://data.ssb.no/api/v0/no/table"
POPULATION_TABLE_ID = "11342"
POPULATION_CONTENT_CODE = "Folkemengde"


def _as_list(values: object | Iterable[object]) -> list[object]:
    if isinstance(values, (str, int)):
        return [values]
    if not isinstance(values, Iterable):
        return [values]
    return list(values)


def _normalize_years(years: object | Iterable[object]) -> list[str]:
    return [str(year).strip() for year in _as_list(years)]


def _post_statbank_query(
    table_id: str,
    query: dict[str, object],
    *,
    timeout: int = 30,
) -> dict[str, object]:
    response = requests.post(
        f"{STATBANK_API_BASE_URL}/{table_id}",
        json=query,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def _population_query(region_ids: list[str], years: list[str]) -> dict[str, object]:
    return {
        "query": [
            {
                "code": "Region",
                "selection": {"filter": "item", "values": region_ids},
            },
            {
                "code": "ContentsCode",
                "selection": {"filter": "item", "values": [POPULATION_CONTENT_CODE]},
            },
            {
                "code": "Tid",
                "selection": {"filter": "item", "values": years},
            },
        ],
        "response": {"format": "JSON-stat2"},
    }


def _jsonstat_population_to_frame(
    data: dict[str, object],
    *,
    region_col: str,
    value_col: str,
) -> pd.DataFrame:
    dimensions = data["dimension"]
    values = data.get("value", [])
    size = data["size"]

    if not isinstance(dimensions, dict) or not isinstance(size, list):
        raise ValueError("Unexpected JSON-stat response from SSB")

    region_ids = list(
        dimensions["Region"]["category"]["index"].keys()  # type: ignore[index]
    )
    years = list(dimensions["Tid"]["category"]["index"].keys())  # type: ignore[index]
    year_count = int(size[2])

    rows = []
    for region_index, region_id in enumerate(region_ids):
        for year_index, year in enumerate(years):
            value_index = region_index * year_count + year_index
            rows.append(
                {
                    region_col: region_id,
                    "år": year,
                    value_col: values[value_index],  # type: ignore[index]
                }
            )

    return pd.DataFrame(rows)


def _current_county_ids() -> list[str]:
    history = load_regions_history()
    return list(
        history.loc[
            (history["nivå"] == "fylke") & (history["er_gjeldende"] == "true"),
            "regionnummer",
        ]
    )


def get_municipality_population(
    years: object | Iterable[object],
    municipality_ids: Optional[Iterable[object]] = None,
    *,
    include_region_info: bool = True,
    timeout: int = 30,
) -> pd.DataFrame:
    """Fetch municipality population per 1 January from SSB table 11342."""
    if municipality_ids is None:
        municipality_ids = load_current_municipalities()["kommunenummer"]

    region_ids = [normalize_municipality_id(value) for value in municipality_ids]
    year_values = _normalize_years(years)
    data = _post_statbank_query(
        POPULATION_TABLE_ID,
        _population_query(region_ids, year_values),
        timeout=timeout,
    )
    population = _jsonstat_population_to_frame(
        data,
        region_col="kommunenummer",
        value_col="folketall",
    )

    if include_region_info:
        return add_municipality_info(population, "kommunenummer")
    return population


def get_county_population(
    years: object | Iterable[object],
    county_ids: Optional[Iterable[object]] = None,
    *,
    timeout: int = 30,
) -> pd.DataFrame:
    """Fetch county population per 1 January from SSB table 11342."""
    if county_ids is None:
        county_ids = _current_county_ids()

    region_ids = [normalize_county_id(value) for value in county_ids]
    year_values = _normalize_years(years)
    data = _post_statbank_query(
        POPULATION_TABLE_ID,
        _population_query(region_ids, year_values),
        timeout=timeout,
    )
    return _jsonstat_population_to_frame(
        data,
        region_col="fylkesnummer",
        value_col="folketall",
    )


def add_municipality_population(
    df: pd.DataFrame,
    *,
    municipality_col: str = "kommunenummer",
    year_col: str = "år",
    population_col: str = "folketall",
    timeout: int = 30,
) -> pd.DataFrame:
    """Add municipality population to a DataFrame by municipality id and year."""
    result = df.copy()
    result["__kommunenummer"] = result[municipality_col].map(normalize_municipality_id)
    result["__år"] = result[year_col].map(lambda year: str(year).strip())

    population = get_municipality_population(
        years=sorted(result["__år"].dropna().unique()),
        municipality_ids=sorted(result["__kommunenummer"].dropna().unique()),
        include_region_info=False,
        timeout=timeout,
    ).rename(
        columns={
            "kommunenummer": "__kommunenummer",
            "år": "__år",
            "folketall": population_col,
        }
    )

    result = result.merge(
        population,
        on=["__kommunenummer", "__år"],
        how="left",
    )
    return result.drop(columns=["__kommunenummer", "__år"])


def add_county_population(
    df: pd.DataFrame,
    *,
    county_col: str = "fylkesnummer",
    year_col: str = "år",
    population_col: str = "folketall",
    timeout: int = 30,
) -> pd.DataFrame:
    """Add county population to a DataFrame by county id and year."""
    result = df.copy()
    result["__fylkesnummer"] = result[county_col].map(normalize_county_id)
    result["__år"] = result[year_col].map(lambda year: str(year).strip())

    population = get_county_population(
        years=sorted(result["__år"].dropna().unique()),
        county_ids=sorted(result["__fylkesnummer"].dropna().unique()),
        timeout=timeout,
    ).rename(
        columns={
            "fylkesnummer": "__fylkesnummer",
            "år": "__år",
            "folketall": population_col,
        }
    )

    result = result.merge(
        population,
        on=["__fylkesnummer", "__år"],
        how="left",
    )
    return result.drop(columns=["__fylkesnummer", "__år"])
