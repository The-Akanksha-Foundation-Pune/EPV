#!/usr/bin/env python3
"""
Script to add expense head data to the ExpenseHead table
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, ExpenseHead
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

# Expense head data
EXPENSE_HEAD_DATA = [
    ("Staff tea and refreshments", "Staff Welfare", "", True),
    ("Staff annual lunch", "Staff Welfare", "", True),
    ("Staff retreat", "Staff Welfare", "", True),
    ("Staff momentos", "Staff Welfare", "", True),
    ("Education Material", "Education Expenses", "", True),
    ("Art Material", "Education Expenses", "", True),
    ("Teachers' reference books", "Education Expenses", "", True),
    ("Science Lab kits and other equipment", "Education Expenses", "", True),
    ("Students' External Evaluation fees & expenses", "Education Expenses", "", True),
    ("Field Trips", "Education Expenses", "", True),
    ("Educational Software Subscriptions", "Education Expenses", "", True),
    ("SDR Expenses", "Education Expenses", "", True),
    ("Exam Fees", "Education Expenses", "", True),
    ("Annual day", "School Events", "", True),
    ("Fairs and Festival Celebrations", "School Events", "", True),
    ("SSC farewell", "School Events", "", True),
    ("Sports Day - Food/Fees", "Sports Expenses", "", True),
    ("Sports Day - Venue", "Sports Expenses", "", True),
    ("Sports Material and Equipment", "Sports Expenses", "", True),
    ("Akanksha Sports event", "Sports Expenses", "", True),
    ("External Sports event", "Sports Expenses", "", True),
    ("Mid-Day Meal Contingency", "603000 - Child Welfare", "", True),
    ("Medical Welfare Expenses", "603001 - Child Welfare", "", True),
    ("School clubs", "603002 - Child Welfare", "", True),
    ("External Visit", "Community Engagement", "", True),
    ("Local Events", "Community Engagement", "", True),
    ("Local Conveyance", "Travel Expenses", "", True),
    ("Domestic Travel", "Travel Expenses", "", True),
    ("International travel", "Travel Expenses", "", True),
    ("Postage & Courier", "Communication", "", True),
    ("Telephone & Internet", "Communication", "", True),
    ("Stationery, photocopying, printing & computer accessories", "Printing & Stationery", "", True),
    ("Rent", "Rent, Electricity And Other Utilities", "", True),
    ("Electricity", "Rent, Electricity And Other Utilities", "", True),
    ("Utility & Water Charges", "Rent, Electricity And Other Utilities", "", True),
    ("Repair costs", "Repairs & Maintenance", "", True),
    ("Maintenance expenses", "Repairs & Maintenance", "", True),
    ("AMC", "Repairs & Maintenance", "", True),
    ("Cleaning & cleaning Supplies", "Repairs & Maintenance", "", True),
    ("Video Creation Expenses", "Communication/Fund Raising Expenses", "", True),
    ("Events", "Communication/Fund Raising Expenses", "", True),
    ("Billdesk Charges", "Communication/Fund Raising Expenses", "", True),
    ("Other Communication Expense", "Communication/Fund Raising Expenses", "", True),
    ("Website Maintenance", "Communication/Fund Raising Expenses", "", True),
    ("Bank Charges", "Other Expenses", "", True),
    ("Other Administrative Expenses", "Other Expenses", "", True),
    ("D & O Insurance", "Other Expenses", "", True),
    ("E & O Policy", "Other Expenses", "", True),
    ("Broadform Liability (CGL)", "Other Expenses", "", True),
    ("Membership & Subscriptions", "Other Expenses", "", True),
    ("Legal Fees", "Legal and Professional Charges", "", True),
    ("Other Legal Expenses", "Legal and Professional Charges", "", True),
    ("Professional Fees", "Legal and Professional Charges", "", True),
    ("Audit Fees", "Legal and Professional Charges", "", True),
    ("Training Events - Edventure", "Training & Capacity Building expenses", "", True),
    ("Other Training Events - Internal", "Training & Capacity Building expenses", "", True),
    ("Other Training Events - External", "Training & Capacity Building expenses", "", True),
    ("Resource person fee", "Training & Capacity Building expenses", "", True),
]

def update_expense_heads():
    """Add new expense head data to the ExpenseHead table"""
    
    with app.app_context():
        try:
            print("Starting expense head data insertion...")
            
            # Insert new expense head data
            print("Inserting new expense head data...")
            inserted_count = 0
            
            for head_name, head_code, description, is_active in EXPENSE_HEAD_DATA:
                # Handle empty description values
                description_value = description if description.strip() else None
                
                expense_head = ExpenseHead(
                    head_name=head_name,
                    head_code=head_code,
                    description=description_value,
                    is_active=is_active
                )
                
                db.session.add(expense_head)
                inserted_count += 1
                print(f"Added: {head_name} ({head_code})")
            
            # Commit all changes
            db.session.commit()
            print(f"\nSuccessfully inserted {inserted_count} expense head records")
            print("Expense head data insertion completed successfully!")
            
        except Exception as e:
            print(f"Error updating expense head data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    update_expense_heads()
