"""
Google Sheets integration for Luckydex.

This module handles reading data from Google Sheets.
"""

import os
import json
import random
import pytz
from datetime import datetime
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
                    'https://www.googleapis.com/auth/spreadsheets',
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


    def _get_or_create_worksheet(self, name: str, headers: Optional[List[str]] = None):
        """Get a worksheet by name, creating it with optional headers if missing."""
        if not self.client:
            raise ValueError("Google Sheets client not initialized")

        spreadsheet = self._get_spreadsheet()
        try:
            return spreadsheet.worksheet(name)
        except Exception:
            # Create worksheet with at least one row for headers if provided
            worksheet = spreadsheet.add_worksheet(title=name, rows=1000, cols=10)
            if headers:
                worksheet.append_row(headers)
            return worksheet


    def save_winner(self, entry: Dict, winners_sheet_name: Optional[str] = None) -> bool:
        """
        Save a winner entry to the winners sheet.
        
        Sheet structure:
        - Column A (index 0): timestamp
        - Column B (index 1): id
        - Column C (index 2): number
        - Column D (index 3): name
        - Column E (index 4): description

        Args:
            entry: Dict with keys id, number, name, description
            winners_sheet_name: Target sheet name for winners (defaults to env or 'Winners')

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.client:
            # In non-configured environments, skip persistence gracefully
            return False

        winners_name = (
            winners_sheet_name
            or os.environ.get('GOOGLE_WINNERS_SHEET_NAME')
            or 'Winners'
        )

        try:
            # Get the worksheet (don't create if it doesn't exist - assume it's already set up)
            spreadsheet = self._get_spreadsheet()
            try:
                worksheet = spreadsheet.worksheet(winners_name)
            except Exception:
                # If sheet doesn't exist, create it with proper headers
                worksheet = spreadsheet.add_worksheet(title=winners_name, rows=1000, cols=10)
                # Set headers: A=timestamp, B=id, C=number, D=name, E=description
                worksheet.append_row(['timestamp', 'id', 'number', 'name', 'description'])
            
            # Check if this entry was already saved (prevent duplicate writes)
            entry_id = str(entry.get('id', '')).strip()
            entry_number = str(entry.get('number', '')).strip()
            
            # Get all winners to check for duplicates
            existing_winners = worksheet.get_all_records()
            for winner in existing_winners[-50:]:  # Check last 50 entries
                winner_id = str(winner.get('id', '')).strip()
                winner_number = str(winner.get('number', '')).strip()
                # If ID matches OR number matches, this was already saved
                if (entry_id and winner_id and entry_id == winner_id) or \
                   (entry_number and winner_number and entry_number == winner_number):
                    # Already saved, skip duplicate write
                    return True
            
            # Find the next empty row in column A (skip header row 1)
            # Get all values in column A to find the last non-empty row
            col_a_values = worksheet.col_values(1)  # Column A is index 1
            next_row = len(col_a_values) + 1  # Next row after last non-empty cell in column A
            
            # If sheet only has header, start at row 2
            if next_row == 2 and col_a_values and col_a_values[0].lower() in ['time', 'timestamp']:
                next_row = 2
            elif next_row < 2:
                next_row = 2
            
            # Prepare the row data - Column A=timestamp, B=id, C=number, D=name, E=description
            myt = pytz.timezone('Asia/Kuala_Lumpur')
            timestamp = datetime.now(myt).strftime('%Y-%m-%d %H:%M:%S')
            row_data = [
                timestamp,                    # Column A
                entry.get('id', ''),          # Column B
                entry.get('number', ''),      # Column C
                entry.get('name', ''),        # Column D
                entry.get('description', ''), # Column E
            ]
            
            # Write to specific row and columns A-E using range notation
            range_name = f'A{next_row}:E{next_row}'
            worksheet.update(range_name, [row_data], value_input_option='RAW')
            return True
        except Exception as e:
            print(f"Error saving winner to Google Sheets: {e}")
            return False


    def get_winners(self, winners_sheet_name: Optional[str] = None) -> List[Dict]:
        """
        Return all winners from the winners sheet, sorted by timestamp (latest first).
        
        Sheet structure (READ ONLY - never writes):
        - Column A: timestamp
        - Column B: id
        - Column C: number
        - Column D: name
        - Column E: description

        Args:
            winners_sheet_name: Target sheet name for winners (defaults to env or 'Winners')

        Returns:
            List of winner dicts, sorted by timestamp in descending order (latest first)
        """
        if not self.client:
            return []

        winners_name = (
            winners_sheet_name
            or os.environ.get('GOOGLE_WINNERS_SHEET_NAME')
            or 'Winners'
        )

        try:
            # Only read from the worksheet - never create or modify
            spreadsheet = self._get_spreadsheet()
            worksheet = spreadsheet.worksheet(winners_name)
            
            # Get all records - assumes headers exist: timestamp, id, number, name, description
            # Column A=timestamp, B=id, C=number, D=name, E=description
            records = worksheet.get_all_records()

            # Sort by timestamp in descending order (latest first)
            def get_timestamp(record: Dict) -> str:
                # Column A is timestamp
                ts = record.get('timestamp') or record.get('Timestamp') or record.get('time') or ''
                return ts

            # Sort in descending order (latest first)
            # Empty timestamps go to the end
            records.sort(key=lambda r: get_timestamp(r) or '', reverse=True)

            return records
        except Exception as e:
            # If sheet doesn't exist, return empty list (don't create it)
            print(f"Error reading winners from Google Sheets: {e}")
            return []


    def get_winner_ids(self, winners_sheet_name: Optional[str] = None) -> List[str]:
        """
        Return a list of winner IDs (as strings) from the winners sheet.
        
        Reads from Column B (id) of the winners sheet.
        """
        winners = self.get_winners(winners_sheet_name)
        ids: List[str] = []
        for w in winners:
            # Column B is 'id' - normalize and fall back to number (Column C) if id missing
            raw_id = w.get('id') or w.get('ID') or w.get('number') or w.get('Number')
            if raw_id is not None and raw_id != '':
                ids.append(str(raw_id))
        return ids

    def get_winner_numbers(self, winners_sheet_name: Optional[str] = None) -> set:
        """
        Return a set of winner numbers (as strings) from the winners sheet.
        
        Reads from Column C (number) of the winners sheet.
        """
        winners = self.get_winners(winners_sheet_name)
        numbers = set()
        for w in winners:
            raw_number = w.get('number') or w.get('Number')
            if raw_number is not None and raw_number != '':
                numbers.add(str(raw_number))
        return numbers


    def get_unique_random_entry(
        self,
        sheet_name: Optional[str] = None,
        winners_sheet_name: Optional[str] = None,
        exclude_ids: Optional[List[str]] = None,
        exclude_numbers: Optional[List[str]] = None
    ) -> Dict:
        """
        Get a random entry that has not won before.

        Args:
            sheet_name: Name of the sheet to read from
            winners_sheet_name: Name of the winners sheet
            exclude_ids: List of IDs to exclude (for session uniqueness)
            exclude_numbers: List of numbers to exclude (for session uniqueness)

        Raises ValueError if no eligible entries remain.
        """
        if not self.client:
            # Fallback to mock when client not initialized
            return self._get_mock_entry()

        # Get all winners from the winners sheet
        winners = self.get_winners(winners_sheet_name)

        # Build sets of all IDs and numbers that have already won (normalized as strings)
        prior_ids = set()
        prior_numbers = set()

        for winner in winners:
            # Get ID from winner record
            winner_id = winner.get('id') or winner.get('ID')
            if winner_id is not None and winner_id != '':
                prior_ids.add(str(winner_id).strip())

            # Get number from winner record
            winner_number = winner.get('number') or winner.get('Number')
            if winner_number is not None and winner_number != '':
                prior_numbers.add(str(winner_number).strip())

        # Add session exclusions (IDs and numbers drawn in current session)
        if exclude_ids:
            prior_ids.update(str(id).strip() for id in exclude_ids if id and id != '')
        if exclude_numbers:
            prior_numbers.update(str(num).strip() for num in exclude_numbers if num and num != '')

        spreadsheet = self._get_spreadsheet()
        # Select worksheet
        if sheet_name:
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)

        records = worksheet.get_all_records()
        if not records:
            raise ValueError("Spreadsheet is empty")

        # Filter out records whose id OR number already won
        eligible: List[Dict] = []
        for r in records:
            candidate_id = r.get('id', r.get('ID', None))
            candidate_number = r.get('number', r.get('Number', None))

            # Normalize values for comparison
            candidate_id_str = str(candidate_id).strip() if candidate_id is not None and candidate_id != '' else None
            candidate_number_str = str(candidate_number).strip() if candidate_number is not None and candidate_number != '' else None

            # Check if ID already won
            id_won = candidate_id_str is not None and candidate_id_str in prior_ids

            # Check if number already won
            number_won = candidate_number_str is not None and candidate_number_str in prior_numbers

            # Only add if neither ID nor number has won before
            if not id_won and not number_won:
                eligible.append(r)

        if not eligible:
            raise ValueError("No eligible entries remaining")

        chosen = random.choice(eligible)
        return {
            'id': chosen.get('id', chosen.get('ID', '')),
            'number': chosen.get('number', chosen.get('Number', '')),
            'name': chosen.get('name', chosen.get('Name', '')),
            'description': chosen.get('description', chosen.get('Description', '')),
            'total_entries': len(records),
            'eligible_entries': len(eligible)
        }

