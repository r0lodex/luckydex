"""
Google Sheets integration for Luckydex.

This module handles reading data from Google Sheets.
"""

import os
import json
import random
from typing import Dict, List, Optional
import gspread
from google.oauth2.service_account import Credentials


class SheetsClient:
    """Client for interacting with Google Sheets."""

    def __init__(self):
        """Initialize the Google Sheets client."""
        self.client = None
        self.spreadsheet = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the gspread client with credentials."""
        try:
            # Try to get credentials from environment variable (JSON string)
            creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')

            if creds_json:
                # Parse JSON from environment variable
                creds_dict = json.loads(creds_json)
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
                credentials = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=scopes
                )
                self.client = gspread.authorize(credentials)
            else:
                print("Warning: No Google Sheets credentials found")

        except Exception as e:
            print(f"Error initializing Google Sheets client: {e}")
            self.client = None

    def _get_spreadsheet(self):
        """Get the spreadsheet by ID or URL from environment."""
        if not self.client:
            raise ValueError("Google Sheets client not initialized")

        if self.spreadsheet:
            return self.spreadsheet

        spreadsheet_id = os.environ.get('GOOGLE_SPREADSHEET_ID')
        spreadsheet_url = os.environ.get('GOOGLE_SPREADSHEET_URL')

        if spreadsheet_id:
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        elif spreadsheet_url:
            self.spreadsheet = self.client.open_by_url(spreadsheet_url)
        else:
            raise ValueError(
                "No spreadsheet ID or URL found in environment variables. "
                "Set GOOGLE_SPREADSHEET_ID or GOOGLE_SPREADSHEET_URL"
            )

        return self.spreadsheet

    def get_random_entry(self, sheet_name: Optional[str] = None) -> Dict:
        """
        Get a random entry from the specified sheet.

        Args:
            sheet_name: Name of the sheet to read from.
            If None, uses the first sheet.

        Returns:
            Dict with keys: id, number, name, description

        Raises:
            ValueError: If the sheet is not found or has invalid format
        """
        if not self.client:
            # Return mock data if client is not initialized (for testing)
            return self._get_mock_entry()

        try:
            spreadsheet = self._get_spreadsheet()

            # Get the specified sheet or the first one
            if sheet_name:
                worksheet = spreadsheet.worksheet(sheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(0)

            # Get all records (assumes first row is header)
            records = worksheet.get_all_records()

            if not records:
                raise ValueError("Spreadsheet is empty")

            # Select a random record
            random_record = random.choice(records)

            # Extract the required fields with fallbacks
            result = {
                'id': random_record.get('id', random_record.get('ID', '')),
                'number': random_record.get('number', random_record.get('Number', '')),
                'name': random_record.get('name', random_record.get('Name', '')),
                'description': random_record.get('description', random_record.get('Description', '')),
                'total_entries': len(records)
            }

            return result

        except Exception as e:
            print(f"Error reading from Google Sheets: {e}")
            raise ValueError(f"Failed to read from spreadsheet: {str(e)}")

    def _get_mock_entry(self) -> Dict:
        """Return mock data for testing when credentials are not available."""
        mock_data = [
            {'id': 1, 'number': 777, 'name': 'Lucky Seven', 'description': 'The luckiest number'},
            {'id': 2, 'number': 888, 'name': 'Fortune Eight', 'description': 'Symbol of prosperity'},
            {'id': 3, 'number': 333, 'name': 'Triple Three', 'description': 'Magic number'},
            {'id': 4, 'number': 999, 'name': 'Cloud Nine', 'description': 'Highest luck'},
            {'id': 5, 'number': 111, 'name': 'New Beginning', 'description': 'Fresh start'},
        ]

        selected = random.choice(mock_data)
        selected['total_entries'] = len(mock_data)
        selected['_mock_data'] = True

        return selected

    def get_all_entries(self, sheet_name: Optional[str] = None) -> List[Dict]:
        """
        Get all entries from the specified sheet.

        Args:
            sheet_name: Name of the sheet to read from.
            If None, uses the first sheet.

        Returns:
            List of dictionaries with entries

        Raises:
            ValueError: If the sheet is not found or has invalid format
        """
        if not self.client:
            raise ValueError("Google Sheets client not initialized")

        spreadsheet = self._get_spreadsheet()

        if sheet_name:
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)

        records = worksheet.get_all_records()
        return records

