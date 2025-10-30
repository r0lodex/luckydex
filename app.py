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
        loader=FileSystemLoader("chalicelib/html")).get_template(file).render(context)


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
    api_url = os.environ.get('API_URL', '')
    if not api_url and hasattr(app.current_request, 'context'):
        # Try to construct from the current request context
        api_url = ''

    # Render the Jinja template
    content = render("home.html", {'api_url': api_url})

    return Response(
        body=content,
        headers={'Content-Type': 'text/html'}
    )

@app.route('/luckydex')
def luckydex():
    """
    Luckydex endpoint that draws a random entry from a Google Spreadsheet.
    The spreadsheet should have columns: id, number, name, description
    Returns a random row with the number and associated data.
    """
    try:
        # Get the sheet name from environment variable or use default (first sheet)
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME')

        # Get random entry from Google Sheets
        entry = sheets_client.get_random_entry(sheet_name)

        return {
            'success': True,
            'id': entry['id'],
            'number': entry['number'],
            'name': entry['name'],
            'description': entry['description'],
            'total_entries': entry.get('total_entries', 0),
            'mock_data': entry.get('_mock_data', False)
        }

    except Exception as e:
        return Response(
            body={
                'success': False,
                'error': str(e),
                'message': 'Failed to draw number from spreadsheet'
            },
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )