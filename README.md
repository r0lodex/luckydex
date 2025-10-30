# Luckydex API

A serverless API built with AWS Chalice, deployed automatically via GitHub Actions.

## Overview

This project provides a RESTful API using AWS Chalice that deploys to AWS Lambda and API Gateway. The deployment is automated through GitHub Actions with support for multiple environments (dev, staging, production).

## Features

- 🚀 Serverless architecture using AWS Lambda
- 🔄 Automatic deployment via GitHub Actions
- 🌍 Multi-environment support (dev, staging, prod)
- 📝 RESTful API endpoints
- ✅ Health check endpoint
- 🔒 AWS credentials management via GitHub Secrets

## Prerequisites

- Python 3.11 or higher
- AWS Account with appropriate permissions
- AWS CLI configured locally (for local development)
- GitHub repository with Actions enabled
- Google Cloud account with Google Sheets API enabled (for Sheets integration)
- A Google Spreadsheet with the required format

## Project Structure

```
luckydex/
├── .chalice/
│   ├── config.json          # Chalice configuration for different stages
│   └── policy-dev.json      # IAM policy template
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions deployment workflow
├── chalicelib/
│   ├── __init__.py
│   └── sheets.py           # Google Sheets integration
├── templates/
│   └── home.html           # Jinja2 template for home page
├── tests/
│   ├── __init__.py
│   └── test_app.py         # Unit tests
├── app.py                  # Main Chalice application
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── Makefile               # Convenient development commands
├── setup.sh               # Setup script
├── pytest.ini             # Pytest configuration
├── GOOGLE_SHEETS_SETUP.md # Detailed Google Sheets setup guide
└── README.md              # This file
```

## Local Development

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd luckydex
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS credentials

Make sure your AWS credentials are configured:

```bash
aws configure
```

### 5. Set up Google Sheets (Optional but Recommended)

To use the Luckydex number drawing feature, you need to set up Google Sheets integration. See the detailed guide in [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md).

Quick setup:
1. Create a Google Cloud project and enable Google Sheets API
2. Create a service account and download credentials as `google-credentials.json`
3. Create a spreadsheet with columns: `id`, `number`, `name`, `description`
4. Share the spreadsheet with your service account email
5. Copy `.env.example` to `.env` and add your spreadsheet ID

**Note**: The app will work without Google Sheets credentials by using mock data for testing.

### 6. Run locally

```bash
chalice local
# or
make run
```

The API will be available at `http://localhost:8000`

Visit `http://localhost:8000/home` to see the interactive web interface!

## API Endpoints

### Root Endpoint
```
GET /
```
Returns welcome message and API status.

### Health Check
```
GET /health
```
Returns service health status.

### Home Page
```
GET /home
```
Returns an interactive HTML page where users can draw random numbers from a Google Spreadsheet. Features a beautiful UI with async JavaScript that calls the `/luckydex` endpoint.

### Luckydex - Draw Random Number
```
GET /luckydex
```
Draws a random entry from a connected Google Spreadsheet and returns the lucky number with associated data.

**Response Example:**
```json
{
  "success": true,
  "id": 1,
  "number": 777,
  "name": "Lucky Seven",
  "description": "The luckiest number of all",
  "total_entries": 5,
  "mock_data": false
}
```

**Note**: The spreadsheet must have columns: `id`, `number`, `name`, `description`

## Deployment

### GitHub Actions Setup

#### 1. Configure GitHub Secrets

Go to your GitHub repository settings and add the following secrets:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: Your preferred AWS region (e.g., `us-east-1`)

**To create AWS credentials for deployment:**

1. Go to AWS IAM Console
2. Create a new user for CI/CD deployment
3. Attach policies: `AWSLambdaFullAccess`, `IAMFullAccess`, `AmazonAPIGatewayAdministrator`
4. Generate access keys
5. Add the keys to GitHub Secrets

#### 2. Deployment Workflow

The GitHub Actions workflow automatically deploys to different environments:

- **Development**: Deploys on push to `develop` branch
- **Staging**: Deploys on push to `main` branch
- **Production**: Deploys after staging, on push to `main` branch

#### 3. Manual Deployment

You can also trigger deployments manually:

1. Go to Actions tab in your GitHub repository
2. Select "Deploy to AWS" workflow
3. Click "Run workflow"

### Manual Deployment (CLI)

#### Deploy to development
```bash
chalice deploy --stage dev
```

#### Deploy to staging
```bash
chalice deploy --stage staging
```

#### Deploy to production
```bash
chalice deploy --stage prod
```

#### Get the deployed URL
```bash
chalice url --stage dev
```

#### Delete a deployment
```bash
chalice delete --stage dev
```

## Environment Variables

Environment variables are configured in `.chalice/config.json` for each stage:

- `STAGE`: Current deployment stage (dev, staging, prod)

Add additional environment variables in the config file as needed:

```json
{
  "stages": {
    "dev": {
      "environment_variables": {
        "STAGE": "dev",
        "YOUR_VAR": "your_value"
      }
    }
  }
}
```

## Monitoring and Logs

### View logs locally
```bash
chalice logs --stage dev
```

### AWS CloudWatch
Logs are automatically sent to CloudWatch. Access them via:
1. AWS Console → CloudWatch → Log Groups
2. Look for `/aws/lambda/luckydex-dev` (or your stage name)

## Testing

### Run tests locally
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests (when you add test files)
pytest tests/
```

## Security Best Practices

1. **Never commit AWS credentials** to the repository
2. **Use IAM roles** with minimal required permissions
3. **Enable API Gateway authentication** for production endpoints
4. **Use AWS Secrets Manager** for sensitive configuration
5. **Enable CloudWatch alarms** for monitoring
6. **Use VPC** if your Lambda needs to access private resources

## Adding New Endpoints

To add a new endpoint, edit `app.py`:

```python
@app.route('/your-endpoint', methods=['GET'])
def your_function():
    return {'message': 'Your response'}
```

Then deploy:
```bash
chalice deploy --stage dev
```

## Troubleshooting

### Deployment fails with permission errors
- Verify your AWS credentials have the necessary permissions
- Check that the IAM user has Lambda, API Gateway, and IAM permissions

### Cannot access API Gateway endpoint
- Check that the deployment completed successfully
- Verify the endpoint URL with `chalice url --stage dev`
- Check CloudWatch logs for errors

### Local development issues
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check AWS credentials are configured: `aws sts get-caller-identity`

## Additional Resources

- [AWS Chalice Documentation](https://aws.github.io/chalice/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue in the GitHub repository.

