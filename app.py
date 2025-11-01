import os
from chalice import Chalice, Response
from jinja2 import Environment, FileSystemLoader
from chalicelib.sheets import SheetsClient

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in Lambda, which is fine

app = Chalice(app_name='luckydex')

# Enable CORS for the API endpoints
app.api.cors = True


def render(file, context):
    return Environment(
        loader=FileSystemLoader("chalicelib/templates")).get_template(file).render(context)


# Initialize Google Sheets client
sheets_client = SheetsClient()


@app.route('/')
def index():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        'message': 'Welcome to Luckydex API',
        'version': '1.0.0',
        'status': 'healthy'
    }


@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        'status': 'healthy',
        'service': 'luckydex'
    }


@app.route('/home')
def home():
    """
    Home endpoint that returns an HTML page with async JavaScript
    that calls /luckydex to draw a random number and display it.
    """
    # Get the API URL from environment or use the current request
    stage = os.environ.get('STAGE', '')

    # Render the Jinja template
    content = render("home.html", {'api_url': stage})

    return Response(
        body=content,
        headers={'Content-Type': 'text/html'}
    )


@app.route('/luckydex', cors=True, methods=['GET'])
def luckydex():
    """
    Luckydex endpoint that draws a random entry from a Google Spreadsheet.
    The spreadsheet should have columns: id, number, name, description
    Returns a random row with the number and associated data.
    
    Query parameters:
    - exclude_ids: Comma-separated list of IDs to exclude (for session uniqueness)
    - exclude_numbers: Comma-separated list of numbers to exclude (for session uniqueness)
    """
    try:
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME')

        # Get excluded IDs and numbers from query parameters (for current session)
        request = app.current_request
        exclude_ids = []
        exclude_numbers = []
        
        if request and request.query_params:
            exclude_ids_str = request.query_params.get('exclude_ids', '')
            exclude_numbers_str = request.query_params.get('exclude_numbers', '')
            
            if exclude_ids_str:
                exclude_ids = [id.strip() for id in exclude_ids_str.split(',') if id.strip()]
            if exclude_numbers_str:
                exclude_numbers = [num.strip() for num in exclude_numbers_str.split(',') if num.strip()]

        # Get a unique random entry (not previously a winner and not in current session)
        winners_sheet_name = os.environ.get('GOOGLE_WINNERS_SHEET_NAME')
        entry = sheets_client.get_unique_random_entry(
            sheet_name, 
            winners_sheet_name,
            exclude_ids=exclude_ids,
            exclude_numbers=exclude_numbers
        )

        # Persist winner to winners sheet (best-effort)
        saved = sheets_client.save_winner(entry, winners_sheet_name)

        body = {
            'success': True,
            'id': entry['id'],
            'number': entry['number'],
            'name': entry['name'],
            'description': entry['description'],
            'total_entries': entry.get('total_entries', 0),
            'mock_data': entry.get('_mock_data', False),
            'winner_saved': saved
        }
        status_code = 200

    except ValueError as e:
        body = {
            'success': False,
            'error': str(e),
            'message': 'No eligible entries remaining'
        }
        status_code = 409
    except Exception as e:
        body = {
            'success': False,
            'error': str(e),
            'message': 'Failed to draw number from spreadsheet'
        }
        status_code = 500

    return Response(
        body=body,
        status_code=status_code,
        headers={
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )


@app.route('/winners', cors=True, methods=['GET'])
def winners():
    """
    Returns the list of saved winners from the winners sheet.
    """
    try:
        winners_sheet_name = os.environ.get('GOOGLE_WINNERS_SHEET_NAME')
        data = sheets_client.get_winners(winners_sheet_name)
        return {
            'success': True,
            'winners': data
        }
    except Exception as e:
        return Response(
            body={
                'success': False,
                'error': str(e),
                'message': 'Failed to fetch winners'
            },
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )