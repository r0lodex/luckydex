#!/bin/bash

# Luckydex Setup Script
# This script helps you set up the development environment

set -e

echo "🚀 Setting up Luckydex development environment..."

# Check if Python 3.11 or higher is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements-dev.txt

# Check if AWS CLI is installed
echo "🔍 Checking for AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI is not installed."
    echo "   Install it from: https://aws.amazon.com/cli/"
else
    echo "✅ AWS CLI is installed"

    # Check if AWS credentials are configured
    if aws sts get-caller-identity &> /dev/null; then
        echo "✅ AWS credentials are configured"
    else
        echo "⚠️  AWS credentials are not configured."
        echo "   Run: aws configure"
    fi
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Configure AWS credentials if not done: aws configure"
echo "  3. Run the app locally: make run"
echo "  4. Run tests: make test"
echo "  5. Deploy to AWS: make deploy-dev"
echo ""
echo "For more information, see README.md"

