import os
from typing import Optional, Sequence

import google.auth
import google.auth.exceptions
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting import numberFormat, set_frozen, textFormat
from gspread_formatting.dataframe import (
    BasicFormatter,
    cellFormat,
    format_with_dataframe,
)

DEFAULT_SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)
DEFAULT_WORKSHEET_ROWS = 1000
DEFAULT_WORKSHEET_COLS = 26


def get_authorized_client(
    credentials_path: Optional[str] = None,
    *,
    use_application_default_credentials: bool = True,
) -> gspread.client.Client:  # type: ignore[no-any-unimported]
    """Get an authorized gspread client.

    The lookup order is:
    1. Explicit ``credentials_path`` argument.
    2. ``GOOGLE_APPLICATION_CREDENTIALS``.
    3. Legacy ``GOOGLE_APPLICATION_CREDENTIALS_PATH``.
    4. Application Default Credentials.
    """
    service_account_path = (
        credentials_path
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_PATH")
    )
    if service_account_path:
        return gspread.service_account(
            filename=service_account_path,
            scopes=list(DEFAULT_SCOPES),
        )

    if use_application_default_credentials:
        try:
            credentials, _ = google.auth.default(scopes=list(DEFAULT_SCOPES))
        except google.auth.exceptions.DefaultCredentialsError as error:
            raise ValueError(
                "Could not authorize Google Sheets client. Set "
                "GOOGLE_APPLICATION_CREDENTIALS, legacy "
                "GOOGLE_APPLICATION_CREDENTIALS_PATH, pass credentials_path, or "
                "configure Application Default Credentials."
            ) from error

        return gspread.authorize(credentials)  # type: ignore[arg-type]

    raise ValueError(
        "Could not authorize Google Sheets client. Set GOOGLE_APPLICATION_CREDENTIALS, "
        "legacy GOOGLE_APPLICATION_CREDENTIALS_PATH, or pass credentials_path."
    )


def open_spreadsheet(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
) -> gspread.spreadsheet.Spreadsheet:
    """Open a Google spreadsheet by key."""
    gc = get_authorized_client()
    return gc.open_by_key(spreadsheet_key)


def open_spreadsheet_by_url(  # type: ignore[no-any-unimported]
    spreadsheet_url: str,
) -> gspread.spreadsheet.Spreadsheet:
    """Open a Google spreadsheet by URL."""
    gc = get_authorized_client()
    return gc.open_by_url(spreadsheet_url)


def open_worksheet_by_name(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
    worksheet_name: str,
) -> gspread.worksheet.Worksheet:
    """Open a worksheet by spreadsheet key and worksheet name."""
    return open_spreadsheet(spreadsheet_key).worksheet(worksheet_name)


def open_worksheet_by_index(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
    worksheet_index: int = 0,
) -> gspread.worksheet.Worksheet:
    """Open a worksheet by spreadsheet key and zero-based worksheet index."""
    worksheet = open_spreadsheet(spreadsheet_key).get_worksheet(worksheet_index)
    if worksheet is None:
        raise gspread.exceptions.WorksheetNotFound(
            f"No worksheet found at index {worksheet_index}"
        )

    return worksheet


def open_worksheet(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
    worksheet_number: int = 0,
    worksheet_name: Optional[str] = None,
) -> gspread.worksheet.Worksheet:
    """Open a Google worksheet by name if provided, otherwise by index."""
    if worksheet_name is not None:
        return open_worksheet_by_name(spreadsheet_key, worksheet_name)

    return open_worksheet_by_index(spreadsheet_key, worksheet_number)


def create_gspreadsheet(  # type: ignore[no-any-unimported]
    title: str, folder_id: str, locale: str = "no_NO"
) -> gspread.spreadsheet.Spreadsheet:
    """Create a spreadsheet in a Google Drive folder."""
    gc = get_authorized_client()
    sheet = gc.create(title, folder_id)
    sheet.update_locale(locale)
    return sheet


def create_spreadsheet(  # type: ignore[no-any-unimported]
    title: str, folder_id: str, locale: str = "no_NO"
) -> gspread.spreadsheet.Spreadsheet:
    """Create a spreadsheet in a Google Drive folder."""
    return create_gspreadsheet(title, folder_id, locale)


def open_or_create_spreadsheet(  # type: ignore[no-any-unimported]
    title: str, folder_id: str, locale: str = "no_NO"
) -> gspread.spreadsheet.Spreadsheet:
    """Open a spreadsheet by title in a folder, or create it if missing."""
    gc = get_authorized_client()
    try:
        return gc.open(title, folder_id)
    except gspread.exceptions.SpreadsheetNotFound:
        return create_spreadsheet(title, folder_id, locale)


def worksheet_exists(  # type: ignore[no-any-unimported]
    spreadsheet: gspread.spreadsheet.Spreadsheet,
    title: str,
) -> bool:
    """Return whether a worksheet exists in a spreadsheet."""
    try:
        spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return False

    return True


def create_worksheet(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
    title: str,
    rows: int = DEFAULT_WORKSHEET_ROWS,
    cols: int = DEFAULT_WORKSHEET_COLS,
) -> gspread.worksheet.Worksheet:
    """Create a new worksheet."""
    return open_spreadsheet(spreadsheet_key).add_worksheet(
        title=title, rows=rows, cols=cols
    )


def open_or_create_worksheet(  # type: ignore[no-any-unimported]
    spreadsheet: gspread.spreadsheet.Spreadsheet,
    title: str,
    rows: int = DEFAULT_WORKSHEET_ROWS,
    cols: int = DEFAULT_WORKSHEET_COLS,
) -> gspread.worksheet.Worksheet:
    """Open a worksheet by title, or create it if missing."""
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def clear_worksheet(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
) -> None:
    """Clear all values in a worksheet."""
    worksheet.clear()


def delete_worksheet_if_exists(  # type: ignore[no-any-unimported]
    spreadsheet: gspread.spreadsheet.Spreadsheet,
    title: str,
) -> None:
    """Delete a worksheet when it exists."""
    try:
        worksheet = spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return

    spreadsheet.del_worksheet(worksheet)


def get_spreadsheet_url(  # type: ignore[no-any-unimported]
    spreadsheet: gspread.spreadsheet.Spreadsheet,
) -> str:
    """Return the browser URL for a spreadsheet."""
    return str(spreadsheet.url)


def share_spreadsheet(  # type: ignore[no-any-unimported]
    spreadsheet: gspread.spreadsheet.Spreadsheet,
    email: str,
    role: str = "writer",
    *,
    notify: bool = False,
) -> None:
    """Share a spreadsheet with a user email."""
    spreadsheet.share(email, perm_type="user", role=role, notify=notify)


def get_dataframe_shape_for_worksheet(  # type: ignore[no-any-unimported]
    dataframe: pd.DataFrame,
    *,
    include_index: bool = True,
    include_column_header: bool = True,
    min_rows: int = 1,
    min_cols: int = 1,
) -> tuple[int, int]:
    """Return worksheet rows and columns required for a DataFrame export."""
    rows = len(dataframe) + int(include_column_header)
    cols = len(dataframe.columns) + int(include_index)
    return max(rows, min_rows), max(cols, min_cols)


def resize_worksheet_to_dataframe(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
    dataframe: pd.DataFrame,
    *,
    include_index: bool = True,
    include_column_header: bool = True,
    min_rows: int = 1,
    min_cols: int = 1,
) -> None:
    """Resize a worksheet to fit a DataFrame export."""
    rows, cols = get_dataframe_shape_for_worksheet(
        dataframe,
        include_index=include_index,
        include_column_header=include_column_header,
        min_rows=min_rows,
        min_cols=min_cols,
    )
    worksheet.resize(rows=rows, cols=cols)


def set_dataframe_to_worksheet(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
    dataframe: pd.DataFrame,
    *,
    include_index: bool = True,
    include_column_header: bool = True,
    resize: bool = True,
    allow_formulas: bool = True,
) -> gspread.worksheet.Worksheet:
    """Write a DataFrame to an existing worksheet."""
    if resize:
        resize_worksheet_to_dataframe(
            worksheet,
            dataframe,
            include_index=include_index,
            include_column_header=include_column_header,
        )

    set_with_dataframe(
        worksheet,
        dataframe,
        include_index=include_index,
        include_column_header=include_column_header,
        resize=resize,
        allow_formulas=allow_formulas,
    )
    return worksheet


def replace_worksheet_with_dataframe(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
    dataframe: pd.DataFrame,
    *,
    include_index: bool = True,
    include_column_header: bool = True,
    resize: bool = True,
    allow_formulas: bool = True,
) -> gspread.worksheet.Worksheet:
    """Clear a worksheet and write a DataFrame to it."""
    clear_worksheet(worksheet)
    return set_dataframe_to_worksheet(
        worksheet,
        dataframe,
        include_index=include_index,
        include_column_header=include_column_header,
        resize=resize,
        allow_formulas=allow_formulas,
    )


def append_dataframe_to_worksheet(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
    dataframe: pd.DataFrame,
    *,
    include_index: bool = False,
    include_column_header: bool = False,
    resize: bool = False,
    allow_formulas: bool = True,
) -> gspread.worksheet.Worksheet:
    """Append a DataFrame to an existing worksheet."""
    set_with_dataframe(
        worksheet,
        dataframe,
        row=get_next_empty_row(worksheet),
        include_index=include_index,
        include_column_header=include_column_header,
        resize=resize,
        allow_formulas=allow_formulas,
    )
    return worksheet


def get_next_empty_row(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
) -> int:
    """Return the first empty row after existing worksheet values."""
    return len(worksheet.get_all_values()) + 1


def save_dataframe_to_spreadsheet_key(  # type: ignore[no-any-unimported]
    dataframe: pd.DataFrame,
    spreadsheet_key: str,
    worksheet_title: str,
    include_index: bool = True,
    include_column_header: bool = True,
    resize: bool = True,
    allow_formulas: bool = True,
    overwrite: bool = True,
) -> gspread.worksheet.Worksheet:
    """Save a DataFrame to a worksheet in a spreadsheet selected by key."""
    rows, cols = get_dataframe_shape_for_worksheet(
        dataframe,
        include_index=include_index,
        include_column_header=include_column_header,
    )
    spreadsheet = open_spreadsheet(spreadsheet_key)
    worksheet = open_or_create_worksheet(spreadsheet, worksheet_title, rows, cols)

    if overwrite:
        return replace_worksheet_with_dataframe(
            worksheet,
            dataframe,
            include_index=include_index,
            include_column_header=include_column_header,
            resize=resize,
            allow_formulas=allow_formulas,
        )

    return append_dataframe_to_worksheet(
        worksheet,
        dataframe,
        include_index=include_index,
        include_column_header=False,
        resize=resize,
        allow_formulas=allow_formulas,
    )


def save_dataframe_to_worksheet(  # type: ignore[no-any-unimported]
    dataframe: pd.DataFrame,
    spreadsheet_title: str,
    folder_id: str,
    worksheet_title: str,
    locale: str = "no_NO",
    include_index: bool = True,
    include_column_header: bool = True,
    resize: bool = True,
    allow_formulas: bool = True,
    overwrite: bool = True,
) -> gspread.worksheet.Worksheet:
    """Save a DataFrame to a worksheet in a spreadsheet selected by title."""
    rows, cols = get_dataframe_shape_for_worksheet(
        dataframe,
        include_index=include_index,
        include_column_header=include_column_header,
    )
    spreadsheet = open_or_create_spreadsheet(spreadsheet_title, folder_id, locale)
    worksheet = open_or_create_worksheet(spreadsheet, worksheet_title, rows, cols)

    if overwrite:
        return replace_worksheet_with_dataframe(
            worksheet,
            dataframe,
            include_index=include_index,
            include_column_header=include_column_header,
            resize=resize,
            allow_formulas=allow_formulas,
        )

    return append_dataframe_to_worksheet(
        worksheet,
        dataframe,
        include_index=include_index,
        include_column_header=False,
        resize=resize,
        allow_formulas=allow_formulas,
    )


def get_worksheet_as_dataframe(  # type: ignore[no-any-unimported]
    spreadsheet_key: str,
    worksheet_number: int = 0,
    worksheet_name: Optional[str] = None,
    **kwargs: object,
) -> pd.DataFrame:
    """Fetch a Google worksheet as a DataFrame."""
    worksheet = open_worksheet(spreadsheet_key, worksheet_number, worksheet_name)
    return get_as_dataframe(worksheet, **kwargs)


def get_standard_column_formats(  # type: ignore[no-any-unimported]
    *,
    text_columns: Optional[Sequence[str]] = None,
    bold_text_columns: Optional[Sequence[str]] = None,
    date_columns: Optional[Sequence[str]] = None,
    date_time_columns: Optional[Sequence[str]] = None,
    int_columns: Optional[Sequence[str]] = None,
    float_columns: Optional[Sequence[str]] = None,
) -> dict[str, object]:
    """Return standard column formats for analysis spreadsheets."""
    norwegian_number_format = numberFormat(
        "NUMBER", "[<10000]#####; [>99999] ### ###; ### ###"
    )
    norwegian_number_format_decimal = numberFormat(
        "NUMBER", "[<10000]#####0.00; [>99999] ### ###0.00; ### ###0.00"
    )

    return (
        {
            column: cellFormat(
                horizontalAlignment="LEFT",
                wrapStrategy="WRAP",
            )
            for column in text_columns or []
        }
        | {
            column: cellFormat(
                horizontalAlignment="LEFT",
                wrapStrategy="WRAP",
                textFormat=textFormat(bold=True),
            )
            for column in bold_text_columns or []
        }
        | {
            column: cellFormat(
                numberFormat=numberFormat("DATE_TIME", "yyyy-mm-dd"),
                horizontalAlignment="LEFT",
            )
            for column in date_columns or []
        }
        | {
            column: cellFormat(
                numberFormat=numberFormat("DATE_TIME", "yyyy-mm-dd hh:mm:ss"),
                horizontalAlignment="LEFT",
            )
            for column in date_time_columns or []
        }
        | {
            column: cellFormat(
                numberFormat=norwegian_number_format,
                horizontalAlignment="RIGHT",
            )
            for column in int_columns or []
        }
        | {
            column: cellFormat(
                numberFormat=norwegian_number_format_decimal,
                horizontalAlignment="RIGHT",
            )
            for column in float_columns or []
        }
    )


def format_worksheet(  # type: ignore[no-any-unimported]
    worksheet: gspread.worksheet.Worksheet,
    df: pd.DataFrame,
    text_columns: Optional[Sequence[str]] = None,
    bold_text_columns: Optional[Sequence[str]] = None,
    date_columns: Optional[Sequence[str]] = None,
    date_time_columns: Optional[Sequence[str]] = None,
    int_columns: Optional[Sequence[str]] = None,
    float_columns: Optional[Sequence[str]] = None,
    frozen_columns: int = 0,
) -> None:
    """Apply standard formatting to a worksheet based on a DataFrame."""
    formatter = BasicFormatter.with_defaults(
        freeze_headers=True,
        column_formats=get_standard_column_formats(
            text_columns=text_columns,
            bold_text_columns=bold_text_columns,
            date_columns=date_columns,
            date_time_columns=date_time_columns,
            int_columns=int_columns,
            float_columns=float_columns,
        ),
    )

    format_with_dataframe(
        worksheet,
        df,
        formatter=formatter,
        include_index=False,
        include_column_header=True,
    )

    if frozen_columns > 0:
        set_frozen(worksheet, cols=frozen_columns)
