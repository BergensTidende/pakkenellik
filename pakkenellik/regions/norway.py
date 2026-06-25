# mypy: disable-error-code=no-any-unimported
from functools import lru_cache
from typing import Iterable, Literal, Optional

import pandas as pd

BORD4_DATA_BASE_URL = (
    "https://raw.githubusercontent.com/BergensTidende/bord4-data/master/data/dist"
)
CURRENT_MUNICIPALITIES_URL = f"{BORD4_DATA_BASE_URL}/norwegian_municipalities.csv"
REGIONS_HISTORY_URL = f"{BORD4_DATA_BASE_URL}/norwegian_regions_history.csv"
REGION_TRANSITIONS_URL = f"{BORD4_DATA_BASE_URL}/norwegian_region_transitions.csv"

RegionLevel = Literal["kommune", "fylke", "municipality", "county"]
Direction = Literal["from", "to", "both"]


@lru_cache(maxsize=8)
def _read_csv(source: str) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    return pd.read_csv(source, dtype=str, keep_default_na=False)


def _normalize_id(value: object, width: int) -> str:
    if pd.isna(value):
        return ""

    value_str = str(value).strip()
    if value_str.endswith(".0") and value_str[:-2].isdigit():
        value_str = value_str[:-2]
    if value_str.isdigit():
        return value_str.zfill(width)
    return value_str


def normalize_municipality_id(value: object) -> str:
    """Normalize a municipality id to four digits."""
    return _normalize_id(value, 4)


def normalize_county_id(value: object) -> str:
    """Normalize a county id to two digits."""
    return _normalize_id(value, 2)


def _normalize_level(level: RegionLevel) -> Literal["kommune", "fylke"]:
    if level in ("municipality", "kommune"):
        return "kommune"
    if level in ("county", "fylke"):
        return "fylke"
    raise ValueError("level must be 'municipality'/'kommune' or 'county'/'fylke'")


def _transition_level(level: RegionLevel) -> Literal["municipality", "county"]:
    return "municipality" if _normalize_level(level) == "kommune" else "county"


def _normalize_region_id(value: object, level: RegionLevel) -> str:
    return (
        normalize_municipality_id(value)
        if _normalize_level(level) == "kommune"
        else normalize_county_id(value)
    )


def _record_from_row(row: pd.Series) -> dict[str, str]:  # type: ignore[no-any-unimported]
    return {str(key): str(value) for key, value in row.items()}


def load_current_municipalities(
    source: str = CURRENT_MUNICIPALITIES_URL,
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Load current Norwegian municipalities from bord4-data."""
    return _read_csv(source).copy()


def load_regions_history(
    source: str = REGIONS_HISTORY_URL,
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Load Norwegian municipality and county history from bord4-data."""
    return _read_csv(source).copy()


def load_region_transitions(
    source: str = REGION_TRANSITIONS_URL,
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Load Norwegian municipality and county transitions from bord4-data."""
    return _read_csv(source).copy()


def get_municipality(municipality_id: object) -> Optional[dict[str, str]]:
    """Return current municipality metadata for a municipality id."""
    municipality_id_str = normalize_municipality_id(municipality_id)
    municipalities = load_current_municipalities()
    match = municipalities.loc[
        municipalities["kommunenummer"] == municipality_id_str, :
    ]
    if match.empty:
        return None
    return _record_from_row(match.iloc[0])


def get_municipality_name(municipality_id: object) -> Optional[str]:
    """Return current municipality name for a municipality id."""
    municipality = get_municipality(municipality_id)
    if municipality is None:
        return None
    return municipality["kommunenavn"]


def get_county(county_id: object) -> Optional[dict[str, str]]:
    """Return current county metadata for a county id."""
    county_id_str = normalize_county_id(county_id)
    history = load_regions_history()
    match = history.loc[
        (history["nivå"] == "fylke")
        & (history["regionnummer"] == county_id_str)
        & (history["er_gjeldende"] == "true"),
        :,
    ]
    if match.empty:
        return None
    return _record_from_row(match.iloc[0])


def get_county_name(county_id: object) -> Optional[str]:
    """Return current county name for a county id."""
    county = get_county(county_id)
    if county is None:
        return None
    return county["regionnavn"]


def get_county_for_municipality(municipality_id: object) -> Optional[dict[str, str]]:
    """Return current county metadata for a current municipality id."""
    municipality = get_municipality(municipality_id)
    if municipality is None:
        return None
    return {
        "fylkesnummer": municipality["fylkesnummer"],
        "fylkesnavn": municipality["fylkesnavn"],
    }


def get_region_history(
    region_id: object,
    level: RegionLevel = "municipality",
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Return historical rows for a municipality or county id."""
    normalized_level = _normalize_level(level)
    normalized_id = _normalize_region_id(region_id, level)
    history = load_regions_history()
    return history.loc[
        (history["nivå"] == normalized_level)
        & (history["regionnummer"] == normalized_id),
        :,
    ].copy()


def get_region_transitions(
    region_id: object,
    level: RegionLevel = "municipality",
    direction: Direction = "both",
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Return transition rows for a municipality or county id."""
    normalized_id = _normalize_region_id(region_id, level)
    transitions = load_region_transitions()
    transitions = transitions.loc[transitions["level"] == _transition_level(level), :]

    if direction == "from":
        mask = transitions["from_id"] == normalized_id
    elif direction == "to":
        mask = transitions["to_id"] == normalized_id
    elif direction == "both":
        mask = (transitions["from_id"] == normalized_id) | (
            transitions["to_id"] == normalized_id
        )
    else:
        raise ValueError("direction must be 'from', 'to' or 'both'")

    return transitions.loc[mask, :].copy()


def trace_region_to_current(
    region_id: object,
    level: RegionLevel = "municipality",
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Return transition rows followed when tracing a region id to current ids."""
    current_ids = {_normalize_region_id(region_id, level)}
    transitions = load_region_transitions()
    transitions = transitions.loc[
        transitions["level"] == _transition_level(level), :
    ].copy()
    rows: list[pd.DataFrame] = []
    seen_states: set[tuple[str, ...]] = set()

    while True:
        state = tuple(sorted(current_ids))
        if state in seen_states:
            break
        seen_states.add(state)

        outgoing = transitions.loc[transitions["from_id"].isin(current_ids), :].copy()
        if outgoing.empty:
            break

        rows.append(outgoing)
        current_ids = (current_ids - set(outgoing["from_id"])) | set(outgoing["to_id"])

    if not rows:
        return transitions.iloc[0:0].copy()
    return pd.concat(rows, ignore_index=True)


def get_current_region_ids(
    region_id: object,
    level: RegionLevel = "municipality",
) -> list[str]:
    """Return current region ids that a historical region id maps to."""
    normalized_id = _normalize_region_id(region_id, level)
    trace = trace_region_to_current(normalized_id, level)
    if trace.empty:
        candidate_ids = {normalized_id}
    else:
        from_ids = set(trace["from_id"])
        to_ids = set(trace["to_id"])
        candidate_ids = (to_ids - from_ids) or to_ids

    if _normalize_level(level) == "kommune":
        current_ids = set(load_current_municipalities()["kommunenummer"])
    else:
        history = load_regions_history()
        current_ids = set(
            history.loc[
                (history["nivå"] == "fylke") & (history["er_gjeldende"] == "true"),
                "regionnummer",
            ]
        )

    return sorted(candidate_ids & current_ids)


def get_current_municipality_ids(municipality_id: object) -> list[str]:
    """Return current municipality ids that a historical municipality id maps to."""
    return get_current_region_ids(municipality_id, "municipality")


def get_current_municipality(
    municipality_id: object,
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Return current municipality rows for a current or historical municipality id."""
    current_ids = get_current_municipality_ids(municipality_id)
    municipalities = load_current_municipalities()
    return municipalities.loc[
        municipalities["kommunenummer"].isin(current_ids), :
    ].copy()


def _with_normalized_column(
    df: pd.DataFrame,  # type: ignore[no-any-unimported]
    column: str,
    normalized_column: str,
    level: RegionLevel,
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    result = df.copy()
    result[normalized_column] = result[column].map(
        lambda value: _normalize_region_id(value, level)
    )
    return result


def add_municipality_info(
    df: pd.DataFrame,  # type: ignore[no-any-unimported]
    municipality_col: str = "kommunenummer",
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Add current municipality and county metadata to a DataFrame."""
    normalized_col = "__kommunenummer"
    result = _with_normalized_column(
        df, municipality_col, normalized_col, "municipality"
    )
    municipalities = load_current_municipalities().rename(
        columns={"kommunenummer": normalized_col}
    )
    result = result.merge(
        municipalities,
        on=normalized_col,
        how="left",
    )
    return result.drop(columns=[normalized_col])


def _current_ids_or_empty(value: object) -> list[str]:
    return get_current_municipality_ids(value) or [""]


def add_current_municipality_info(
    df: pd.DataFrame,  # type: ignore[no-any-unimported]
    municipality_col: str = "kommunenummer",
) -> pd.DataFrame:  # type: ignore[no-any-unimported]
    """Add current municipality metadata for current or historical municipality ids.

    Rows are duplicated when one historical code maps to multiple current
    municipalities.
    """
    result = df.copy()
    result["current_kommunenummer"] = result[municipality_col].map(
        _current_ids_or_empty
    )
    result = result.explode("current_kommunenummer")

    municipalities = load_current_municipalities().rename(
        columns={
            "kommunenummer": "current_kommunenummer",
            "kommunenavn": "current_kommunenavn",
            "fylkesnummer": "current_fylkesnummer",
            "fylkesnavn": "current_fylkesnavn",
            "siste_endret": "current_siste_endret",
        }
    )
    return result.merge(municipalities, on="current_kommunenummer", how="left")


def _normalize_many(values: Iterable[object], level: RegionLevel) -> list[str]:
    return [_normalize_region_id(value, level) for value in values]
