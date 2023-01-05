import json
import os
from typing import Dict, List, Optional, Union

import gspread
from google.oauth2.service_account import Credentials

SAMPLE_SPREADSHEET_ID = "1mngt0hss_ZCwCPOs-mI5mipKfxAyqmH8Vf_mlBdAmF0"
SHEET_NUM = 0


def load_credentials() -> Optional[Credentials]:  # type: ignore [no-any-unimported]
    """
    Load Google credentials from environment variable

    Returns:
        Credentials: Google credentials
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    if env_credentials := os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return Credentials.from_service_account_info(
            json.loads(env_credentials), scopes=scopes
        )
    else:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")


def get_authorized_client() -> gspread.client.Client:  # type: ignore
    """
    Get authorized client

    Returns:
        gspread.client.Client: authorized client
    """
    if credentials := load_credentials():
        return gspread.authorize(credentials)
    else:
        raise ValueError("No credentials found")


def get_sheet_records(
    spreadsheet_key: str, sheet_num: int = 0, sheet_name: Optional[str] = None
) -> List[Dict[str, Union[str, int]]]:
    """
    Fetch Google spreadsheet as records

    Args:
        spreadsheet_key (str): Google spreadsheet key
        sheet_num (int): Sheet number
        sheet_name (str): Sheet name

      Returns:
        List[Dict]: List of records
    """

    gc = get_authorized_client()

    sheet = gc.open_by_key(spreadsheet_key).get_worksheet(sheet_num)

    return sheet.get_all_records()


def open_sheet(  # type: ignore [no-any-unimported]
    spreadsheet_key: str, sheet_num: int = 0, sheet_name: Optional[str] = None
) -> gspread.worksheet.Worksheet:

    """
    Open Google worksheet

    Args:
        spreadsheet_key (str): Key of the spreadsheet to open.
        sheet_num (int): _description_. Defaults to 0.
        sheet_name (str, optional): Defaults to None.

    Returns:
        gspread.spreadsheet.Spreadsheet: the spreadsheet
    """
    gc = get_authorized_client()

    if sheet_name:
        return gc.open_by_key(spreadsheet_key).worksheet(sheet_name)

    else:
        return gc.open_by_key(spreadsheet_key).get_worksheet(sheet_num)


def open_spreadsheet(  # type: ignore [no-any-unimported]
    spreadsheet_key: str,
) -> gspread.spreadsheet.Spreadsheet:
    """Open Google spreadsheet

    Args:
        spreadsheet_key (str): the key of the spreadsheet to open

    Returns:
        gspread.spreadsheet.Spreadsheet: the spreadsheet
    """

    gc = get_authorized_client()
    return gc.open_by_key(spreadsheet_key)


def create_gspreadsheet(  # type: ignore [no-any-unimported]
    title: str, folder_id: str
) -> gspread.spreadsheet.Spreadsheet:
    """Create a new spreadsheet

    Args:
        title (str): Title of the spradsheet
        folder_id (str): the folder to create the spreadsheet in

    Returns:
        gspread.spreadsheet.Spreadsheet: The created spreadsheet
    """

    gc = get_authorized_client()
    return gc.create(title, folder_id)
