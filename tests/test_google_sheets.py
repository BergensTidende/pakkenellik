from unittest.mock import MagicMock

import pandas as pd
import pytest

gspread = pytest.importorskip("gspread")
sheets = pytest.importorskip("pakkenellik.google.sheets")


def test_get_authorized_client_prefers_standard_google_env(monkeypatch) -> None:
    client = object()
    service_account = MagicMock(return_value=client)
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/google.json")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS_PATH", "/tmp/legacy.json")
    monkeypatch.setattr(sheets.gspread, "service_account", service_account)

    result = sheets.get_authorized_client(
        use_application_default_credentials=False,
    )

    assert result is client
    service_account.assert_called_once_with(
        filename="/tmp/google.json",
        scopes=list(sheets.DEFAULT_SCOPES),
    )


def test_get_authorized_client_supports_legacy_env(monkeypatch) -> None:
    client = object()
    service_account = MagicMock(return_value=client)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS_PATH", "/tmp/legacy.json")
    monkeypatch.setattr(sheets.gspread, "service_account", service_account)

    result = sheets.get_authorized_client(
        use_application_default_credentials=False,
    )

    assert result is client
    service_account.assert_called_once_with(
        filename="/tmp/legacy.json",
        scopes=list(sheets.DEFAULT_SCOPES),
    )


def test_get_authorized_client_uses_adc(monkeypatch) -> None:
    client = object()
    authorize = MagicMock(return_value=client)
    default = MagicMock(return_value=("credentials", "project"))
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS_PATH", raising=False)
    monkeypatch.setattr(sheets.google.auth, "default", default)
    monkeypatch.setattr(sheets.gspread, "authorize", authorize)

    result = sheets.get_authorized_client()

    assert result is client
    default.assert_called_once_with(scopes=list(sheets.DEFAULT_SCOPES))
    authorize.assert_called_once_with("credentials")


def test_open_worksheet_by_index_raises_when_index_is_missing(monkeypatch) -> None:
    spreadsheet = MagicMock()
    spreadsheet.get_worksheet.return_value = None
    monkeypatch.setattr(sheets, "open_spreadsheet", MagicMock(return_value=spreadsheet))

    with pytest.raises(gspread.exceptions.WorksheetNotFound):
        sheets.open_worksheet_by_index("spreadsheet-key", 99)


def test_create_worksheet_uses_configurable_size(monkeypatch) -> None:
    worksheet = object()
    spreadsheet = MagicMock()
    spreadsheet.add_worksheet.return_value = worksheet
    monkeypatch.setattr(sheets, "open_spreadsheet", MagicMock(return_value=spreadsheet))

    result = sheets.create_worksheet("spreadsheet-key", "Data", rows=12, cols=4)

    assert result is worksheet
    spreadsheet.add_worksheet.assert_called_once_with(title="Data", rows=12, cols=4)


def test_open_or_create_worksheet_creates_missing_sheet_with_size() -> None:
    worksheet = object()
    spreadsheet = MagicMock()
    spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound()
    spreadsheet.add_worksheet.return_value = worksheet

    result = sheets.open_or_create_worksheet(spreadsheet, "Data", rows=12, cols=4)

    assert result is worksheet
    spreadsheet.add_worksheet.assert_called_once_with(title="Data", rows=12, cols=4)


def test_get_dataframe_shape_for_worksheet_counts_headers_and_index() -> None:
    dataframe = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    assert sheets.get_dataframe_shape_for_worksheet(dataframe) == (3, 3)
    assert sheets.get_dataframe_shape_for_worksheet(
        dataframe,
        include_index=False,
        include_column_header=False,
    ) == (2, 2)


def test_replace_worksheet_clears_resizes_and_writes(monkeypatch) -> None:
    dataframe = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    worksheet = MagicMock()
    set_with_dataframe = MagicMock()
    monkeypatch.setattr(sheets, "set_with_dataframe", set_with_dataframe)

    result = sheets.replace_worksheet_with_dataframe(
        worksheet,
        dataframe,
        include_index=False,
    )

    assert result is worksheet
    worksheet.clear.assert_called_once_with()
    worksheet.resize.assert_called_once_with(rows=3, cols=2)
    set_with_dataframe.assert_called_once_with(
        worksheet,
        dataframe,
        include_index=False,
        include_column_header=True,
        resize=True,
        allow_formulas=True,
    )


def test_append_dataframe_to_worksheet_uses_first_empty_row(monkeypatch) -> None:
    dataframe = pd.DataFrame({"a": [1, 2]})
    worksheet = MagicMock()
    worksheet.get_all_values.return_value = [["existing"], ["row"]]
    set_with_dataframe = MagicMock()
    monkeypatch.setattr(sheets, "set_with_dataframe", set_with_dataframe)

    result = sheets.append_dataframe_to_worksheet(worksheet, dataframe)

    assert result is worksheet
    set_with_dataframe.assert_called_once_with(
        worksheet,
        dataframe,
        row=3,
        include_index=False,
        include_column_header=False,
        resize=False,
        allow_formulas=True,
    )


def test_save_dataframe_to_spreadsheet_key_creates_dataframe_sized_worksheet(
    monkeypatch,
) -> None:
    dataframe = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    worksheet = MagicMock()
    spreadsheet = MagicMock()
    spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound()
    spreadsheet.add_worksheet.return_value = worksheet
    set_with_dataframe = MagicMock()
    monkeypatch.setattr(sheets, "open_spreadsheet", MagicMock(return_value=spreadsheet))
    monkeypatch.setattr(sheets, "set_with_dataframe", set_with_dataframe)

    result = sheets.save_dataframe_to_spreadsheet_key(
        dataframe,
        "spreadsheet-key",
        "Data",
        include_index=False,
    )

    assert result is worksheet
    spreadsheet.add_worksheet.assert_called_once_with(title="Data", rows=3, cols=2)
    worksheet.clear.assert_called_once_with()
    worksheet.resize.assert_called_once_with(rows=3, cols=2)


def test_save_dataframe_to_worksheet_appends_without_column_header(monkeypatch) -> None:
    dataframe = pd.DataFrame({"a": [1, 2]})
    worksheet = MagicMock()
    worksheet.get_all_values.return_value = [["a"], ["1"]]
    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = worksheet
    set_with_dataframe = MagicMock()
    monkeypatch.setattr(
        sheets,
        "open_or_create_spreadsheet",
        MagicMock(return_value=spreadsheet),
    )
    monkeypatch.setattr(sheets, "set_with_dataframe", set_with_dataframe)

    result = sheets.save_dataframe_to_worksheet(
        dataframe,
        "Spreadsheet",
        "folder-id",
        "Data",
        overwrite=False,
    )

    assert result is worksheet
    worksheet.clear.assert_not_called()
    set_with_dataframe.assert_called_once_with(
        worksheet,
        dataframe,
        row=3,
        include_index=True,
        include_column_header=False,
        resize=True,
        allow_formulas=True,
    )


def test_delete_worksheet_if_exists_deletes_existing_sheet() -> None:
    worksheet = object()
    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = worksheet

    sheets.delete_worksheet_if_exists(spreadsheet, "Data")

    spreadsheet.del_worksheet.assert_called_once_with(worksheet)


def test_delete_worksheet_if_exists_ignores_missing_sheet() -> None:
    spreadsheet = MagicMock()
    spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound()

    sheets.delete_worksheet_if_exists(spreadsheet, "Data")

    spreadsheet.del_worksheet.assert_not_called()


def test_share_spreadsheet_uses_user_permission() -> None:
    spreadsheet = MagicMock()

    sheets.share_spreadsheet(spreadsheet, "person@example.com", role="reader")

    spreadsheet.share.assert_called_once_with(
        "person@example.com",
        perm_type="user",
        role="reader",
        notify=False,
    )
