from unittest.mock import MagicMock

from pakkenellik.integration import client


def test_get_or_create_chart_uses_id_from_copied_chart_dict(monkeypatch) -> None:
    dw = MagicMock()
    dw.copy_chart.return_value = {"id": "copied-chart"}
    monkeypatch.setattr(client, "read_integrations", MagicMock(return_value={}))

    result = client.get_or_create_chart(
        dw,
        key="my-chart",
        copy_from="template-chart",
    )

    assert result == "copied-chart"
    dw.copy_chart.assert_called_once_with("template-chart")


def test_get_or_create_chart_still_accepts_copied_chart_id_string(monkeypatch) -> None:
    dw = MagicMock()
    dw.copy_chart.return_value = "copied-chart"
    monkeypatch.setattr(client, "read_integrations", MagicMock(return_value={}))

    result = client.get_or_create_chart(
        dw,
        key="my-chart",
        copy_from="template-chart",
    )

    assert result == "copied-chart"


def test_get_or_create_chart_raises_without_chart_id(monkeypatch) -> None:
    dw = MagicMock()
    dw.copy_chart.return_value = {"missing": "id"}
    monkeypatch.setattr(client, "read_integrations", MagicMock(return_value={}))

    try:
        client.get_or_create_chart(
            dw,
            key="my-chart",
            copy_from="template-chart",
        )
    except ValueError as error:
        assert str(error) == "Did not receive chart id from Datawrapper API"
    else:
        raise AssertionError("Expected ValueError")
