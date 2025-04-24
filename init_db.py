#!/usr/bin/env python3
"""
Initialize the PostgreSQL database for the Context-Aware Privacy Blurring application.
This script creates all tables and populates them with default data.
"""

import os
from utils.database import init_database

def main():
    """Main function to initialize the database"""
    print("Checking for DATABASE_URL...")
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable not found.")
        print("Please make sure the PostgreSQL database is properly set up.")
        return False
    
    print("Initializing database...")
    try:
        db_manager = init_database()
        print("Database initialized successfully!")
        print("Created default blur rules and sensitive keyword lists.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Database setup complete. You can now run the application.")
    else:
        print("Database setup failed. Please check the error messages above.")