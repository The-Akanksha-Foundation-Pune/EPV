#!/usr/bin/env python3
"""
Script to insert employee data from CSV file to the EmployeeDetails table

NOTE: As of the latest update, employee data from 'uploads/Employee Details.csv'
is automatically loaded as default data when the EmployeeDetails table is created.
This script is now primarily useful for:
- Updating existing employee data with new information
- Adding new employees after initial setup
- Re-syncing data if the CSV file is updated

The script reads from 'uploads/Employee Details.csv' and:
- Inserts new employees not in the database
- Updates existing employees with new information
- Handles role assignments and manager hierarchies
"""

import os
import sys
import csv
from datetime import datetime

# Add the current directory to Python path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, EmployeeDetails
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app for database context
app = Flask(__name__)

# Database configuration
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT', '3306')
db_name = os.environ.get('DB_NAME')

# URL encode the password to handle special characters
import urllib.parse
encoded_password = urllib.parse.quote_plus(db_password) if db_password else ''

# Construct the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def read_csv_file():
    """Read the CSV file from uploads folder"""
    csv_file_path = os.path.join('uploads', 'Employee Details.csv')

    if not os.path.exists(csv_file_path):
        print(f"ERROR: CSV file not found at {csv_file_path}")
        print("Please ensure the file 'Employee Details.csv' exists in the 'uploads' folder")
        return None

    try:
        # Read CSV file using built-in csv module
        data = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            columns = csv_reader.fieldnames
            print(f"Columns found: {columns}")

            for row in csv_reader:
                data.append(row)

        print(f"Successfully read CSV file with {len(data)} rows")
        return data, columns
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {e}")
        return None

def clean_and_validate_data(data, columns):
    """Clean and validate the CSV data"""
    if data is None:
        return None

    # Convert column names to lowercase and replace spaces with underscores
    cleaned_columns = [col.lower().replace(' ', '_').replace('-', '_') for col in columns]

    print(f"Cleaned column names: {cleaned_columns}")

    # Expected columns (flexible mapping)
    column_mapping = {
        'email': ['email', 'email_id', 'email_address'],
        'employee_id': ['employee_id', 'emp_id', 'id'],
        'manager': ['manager', 'manager_email', 'reporting_manager'],
        'manager_name': ['manager_name', 'manager_full_name', 'reporting_manager_name'],
        'name': ['name', 'full_name', 'employee_name'],
        'role': ['role', 'designation', 'position', 'job_title'],
        'is_active': ['is_active', 'active', 'status']
    }

    # Map columns
    mapped_columns = {}
    for target_col, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in cleaned_columns:
                # Find the original column name
                original_col = columns[cleaned_columns.index(possible_name)]
                mapped_columns[target_col] = original_col
                break

    print(f"Column mapping: {mapped_columns}")

    # Check if we have at least email column
    if 'email' not in mapped_columns:
        print("ERROR: No email column found. Please ensure the CSV has an 'email' column")
        return None

    # Create cleaned data
    cleaned_data = []
    for index, row in enumerate(data):
        employee_data = {}

        # Map each column
        for target_col, source_col in mapped_columns.items():
            value = row.get(source_col, '').strip() if row.get(source_col) else ''

            # Special handling for different columns
            if target_col == 'email':
                value = value.lower() if value else ''
            elif target_col == 'is_active':
                # Convert various representations to boolean
                if isinstance(value, str):
                    value = value.lower() in ['true', 'yes', '1', 'active', 'y']
                else:
                    value = True  # Default to active

            employee_data[target_col] = value

        # Set defaults for missing columns
        if 'employee_id' not in employee_data:
            employee_data['employee_id'] = ''
        if 'manager' not in employee_data:
            employee_data['manager'] = ''
        if 'manager_name' not in employee_data:
            employee_data['manager_name'] = ''
        if 'name' not in employee_data:
            employee_data['name'] = ''
        if 'role' not in employee_data:
            employee_data['role'] = 'user'  # Default role
        if 'is_active' not in employee_data:
            employee_data['is_active'] = True

        # Skip rows without email
        if not employee_data['email']:
            print(f"Skipping row {index + 1}: No email provided")
            continue

        cleaned_data.append(employee_data)

    print(f"Cleaned and validated {len(cleaned_data)} employee records")
    return cleaned_data

def update_employees_from_csv():
    """Insert employee data from CSV file"""
    
    with app.app_context():
        try:
            print("Starting employee data insertion from CSV...")

            # Read CSV file
            csv_result = read_csv_file()
            if csv_result is None:
                return

            data, columns = csv_result

            # Clean and validate data
            employee_data = clean_and_validate_data(data, columns)
            if not employee_data:
                print("No valid employee data to insert")
                return
            
            # Insert employee data
            print("Inserting employee data...")
            inserted_count = 0
            updated_count = 0
            skipped_count = 0
            
            for emp_data in employee_data:
                email = emp_data['email']
                
                # Check if employee already exists
                existing_employee = EmployeeDetails.query.filter_by(email=email).first()
                
                if existing_employee:
                    # Update existing employee
                    existing_employee.employee_id = emp_data['employee_id'] or existing_employee.employee_id
                    existing_employee.manager = emp_data['manager'].lower() if emp_data['manager'] else existing_employee.manager
                    existing_employee.manager_name = emp_data['manager_name'] or existing_employee.manager_name
                    existing_employee.name = emp_data['name'] or existing_employee.name
                    existing_employee.role = emp_data['role'] or existing_employee.role
                    existing_employee.is_active = emp_data['is_active']
                    
                    updated_count += 1
                    print(f"Updated: {email} - {emp_data['name']}")
                else:
                    # Create new employee
                    employee = EmployeeDetails(
                        email=email,
                        employee_id=emp_data['employee_id'],
                        manager=emp_data['manager'].lower() if emp_data['manager'] else None,
                        manager_name=emp_data['manager_name'],
                        name=emp_data['name'],
                        role=emp_data['role'],
                        is_active=emp_data['is_active']
                    )
                    
                    db.session.add(employee)
                    inserted_count += 1
                    print(f"Added: {email} - {emp_data['name']} ({emp_data['role']})")
            
            # Commit all changes
            db.session.commit()
            print(f"\nEmployee data processing completed successfully!")
            print(f"- Inserted: {inserted_count} new employees")
            print(f"- Updated: {updated_count} existing employees")
            print(f"- Total processed: {inserted_count + updated_count}")
            
        except Exception as e:
            print(f"Error processing employee data: {e}")
            db.session.rollback()
            raise

def show_csv_sample():
    """Show a sample of what the CSV should look like"""
    print("\n" + "="*60)
    print("EXPECTED CSV FORMAT:")
    print("="*60)
    print("The CSV file should have columns like:")
    print("- email (required)")
    print("- employee_id (optional)")
    print("- manager (optional - manager's email)")
    print("- manager_name (optional)")
    print("- name (optional)")
    print("- role (optional - defaults to 'user')")
    print("- is_active (optional - defaults to True)")
    print("\nExample CSV content:")
    print("email,employee_id,manager,manager_name,name,role,is_active")
    print("john.doe@akanksha.org,EMP001,manager@akanksha.org,Manager Name,John Doe,Finance,True")
    print("jane.smith@akanksha.org,EMP002,supervisor@akanksha.org,Supervisor Name,Jane Smith,Super Admin,True")
    print("="*60)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        show_csv_sample()
    else:
        update_employees_from_csv()
