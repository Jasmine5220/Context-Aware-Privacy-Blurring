#!/bin/bash

echo "Setting up Context-Aware Privacy Blurring system..."

# Check if python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r dependencies.txt

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit the .env file with your database credentials."
fi

# Initialize database if requested
read -p "Do you want to initialize the database now? (y/n): " initialize_db
if [ "$initialize_db" = "y" ] || [ "$initialize_db" = "Y" ]; then
    echo "Initializing database..."
    python init_db.py
fi

echo "Setup complete! You can now run the application with: streamlit run app.py"