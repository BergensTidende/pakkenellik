import pandas as pd

from pakkenellik.regions import norway


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
            {
                "kommunenummer": "5001",
                "kommunenavn": "Split A",
                "fylkesnummer": "50",
                "fylkesnavn": "Test",
                "siste_endret": "2020",
            },
            {
                "kommunenummer": "5002",
                "kommunenavn": "Split B",
                "fylkesnummer": "50",
                "fylkesnavn": "Test",
                "siste_endret": "2020",
            },
        ]
    )


def _history() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "nivå": "fylke",
                "regionnummer": "14",
                "regionnavn": "Sogn og Fjordane",
                "fylkesnummer": "14",
                "fylkesnavn": "Sogn og Fjordane",
                "gyldig_fra": "1919-01-01",
                "gyldig_til": "2020-01-01",
                "er_gjeldende": "false",
            },
            {
                "nivå": "fylke",
                "regionnummer": "46",
                "regionnavn": "Vestland",
                "fylkesnummer": "46",
                "fylkesnavn": "Vestland",
                "gyldig_fra": "2020-01-01",
                "gyldig_til": "",
                "er_gjeldende": "true",
            },
            {
                "nivå": "kommune",
                "regionnummer": "1412",
                "regionnavn": "Solund",
                "fylkesnummer": "14",
                "fylkesnavn": "Sogn og Fjordane",
                "gyldig_fra": "1924-01-01",
                "gyldig_til": "2020-01-01",
                "er_gjeldende": "false",
            },
            {
                "nivå": "kommune",
                "regionnummer": "4636",
                "regionnavn": "Solund",
                "fylkesnummer": "46",
                "fylkesnavn": "Vestland",
                "gyldig_fra": "2020-01-01",
                "gyldig_til": "",
                "er_gjeldende": "true",
            },
        ]
    )


def _transitions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "from_year": "2017",
                "to_year": "2021",
                "level": "municipality",
                "from_id": "1412",
                "to_id": "4636",
                "change_type": "renumbered",
                "source_file": "kommuner_2017_2021.json",
            },
            {
                "from_year": "2017",
                "to_year": "2021",
                "level": "municipality",
                "from_id": "9999",
                "to_id": "5001",
                "change_type": "split",
                "source_file": "test.json",
            },
            {
                "from_year": "2017",
                "to_year": "2021",
                "level": "municipality",
                "from_id": "9999",
                "to_id": "5002",
                "change_type": "split",
                "source_file": "test.json",
            },
            {
                "from_year": "2020",
                "to_year": "2021",
                "level": "county",
                "from_id": "14",
                "to_id": "46",
                "change_type": "merge",
                "source_file": "fylker_2020_2021.json",
            },
        ]
    )


def _patch_region_data(monkeypatch) -> None:
    monkeypatch.setattr(
        norway,
        "load_current_municipalities",
        _current_municipalities,
    )
    monkeypatch.setattr(norway, "load_regions_history", _history)
    monkeypatch.setattr(norway, "load_region_transitions", _transitions)


def test_get_municipality_and_county_names(monkeypatch) -> None:
    _patch_region_data(monkeypatch)

    assert norway.get_municipality_name(4636) == "Solund"
    assert norway.get_county_name(46) == "Vestland"
    assert norway.get_county_for_municipality("4636") == {
        "fylkesnummer": "46",
        "fylkesnavn": "Vestland",
    }


def test_get_region_history_for_old_municipality_code(monkeypatch) -> None:
    _patch_region_data(monkeypatch)

    result = norway.get_region_history("1412")

    assert result.iloc[0]["regionnavn"] == "Solund"
    assert result.iloc[0]["fylkesnavn"] == "Sogn og Fjordane"


def test_get_region_transitions_and_current_municipality(monkeypatch) -> None:
    _patch_region_data(monkeypatch)

    transitions = norway.get_region_transitions("1412")
    current = norway.get_current_municipality("1412")

    assert transitions.iloc[0]["to_id"] == "4636"
    assert norway.get_current_municipality_ids("1412") == ["4636"]
    assert current.iloc[0]["kommunenavn"] == "Solund"
    assert current.iloc[0]["fylkesnavn"] == "Vestland"


def test_current_region_ids_can_return_multiple_ids_for_split(monkeypatch) -> None:
    _patch_region_data(monkeypatch)

    assert norway.get_current_municipality_ids("9999") == ["5001", "5002"]


def test_add_municipality_info_adds_current_county_metadata(monkeypatch) -> None:
    _patch_region_data(monkeypatch)
    df = pd.DataFrame({"kommunenummer": ["4636"]})

    result = norway.add_municipality_info(df)

    assert result.iloc[0]["kommunenavn"] == "Solund"
    assert result.iloc[0]["fylkesnummer"] == "46"
    assert result.iloc[0]["fylkesnavn"] == "Vestland"


def test_add_current_municipality_info_maps_old_code_to_current_code(
    monkeypatch,
) -> None:
    _patch_region_data(monkeypatch)
    df = pd.DataFrame({"kommunenummer": ["1412"]})

    result = norway.add_current_municipality_info(df)

    assert result.iloc[0]["current_kommunenummer"] == "4636"
    assert result.iloc[0]["current_kommunenavn"] == "Solund"
    assert result.iloc[0]["current_fylkesnavn"] == "Vestland"
