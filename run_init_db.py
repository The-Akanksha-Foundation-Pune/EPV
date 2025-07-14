#!/usr/bin/env python3
"""
Script to run init_db on the server database
This will create all EPV tables and populate them with initial data
"""
import os
import sys
from flask import Flask
import urllib.parse

# Add current directory to path so we can import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our models and init_db function
from models import db, init_db

# Fetch DB credentials from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')

# Example for SQLAlchemy URI (adjust as needed for your DB type)
if DB_HOST and DB_USER and DB_PASSWORD and DB_NAME:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT or 3306}/{DB_NAME}"
else:
    # Fallback to SQLite for local dev if env vars are not set
    SQLALCHEMY_DATABASE_URI = 'sqlite:///epv.db'


def create_app_for_server():
    """Create Flask app configured for server database"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'temp-secret-for-init'
    
    # Initialize database with app
    db.init_app(app)
    
    print(f"✅ Flask app configured for server database")
    print(f"   Host: {DB_HOST}")
    print(f"   Database: {DB_NAME}")
    print(f"   User: {DB_USER}")
    
    return app

def run_init_db():
    """Run the init_db function on server database"""
    
    print("🚀 Running init_db on server database...")
    print("=" * 50)
    
    # Create Flask app for server
    app = create_app_for_server()
    
    try:
        with app.app_context():
            print("📋 Creating all database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            print("\n🔧 Running init_db to populate initial data...")
            
            # Run init_db function
            init_db(app)
            
            print("\n🎉 init_db completed successfully!")
            print("\n📊 Summary of what was created:")
            print("   ✅ All EPV application tables")
            print("   ✅ Cost centers with default data")
            print("   ✅ Employee details")
            print("   ✅ Finance settings")
            print("   ✅ Expense heads")
            print("   ✅ All relationships and constraints")
            
            return True
            
    except Exception as e:
        print(f"❌ Error running init_db: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def verify_tables_created():
    """Verify that tables were created successfully"""
    
    print("\n🔍 Verifying tables were created...")
    
    app = create_app_for_server()
    
    try:
        with app.app_context():
            # Import models to check
            from models import (
                CostCenter, EmployeeDetails, ExpenseHead, EPV,
                EPVItem, EPVApproval, EPVAllocation, FinanceEntry,
                SupplementaryDocument, SettingsFinance
            )
            
            # Check each table
            tables_to_check = [
                ('costcenter', CostCenter),
                ('employee_details', EmployeeDetails),
                ('expense_head', ExpenseHead),
                ('epv', EPV),
                ('epv_item', EPVItem),
                ('epv_approval', EPVApproval),
                ('epv_allocation', EPVAllocation),
                ('finance_entry', FinanceEntry),
                ('supplementary_document', SupplementaryDocument),
                ('settings_finance', SettingsFinance)
            ]
            
            print("\n📋 Table verification:")
            all_good = True
            
            for table_name, model_class in tables_to_check:
                try:
                    count = model_class.query.count()
                    print(f"   ✅ {table_name}: {count} records")
                except Exception as e:
                    print(f"   ❌ {table_name}: Error - {e}")
                    all_good = False
            
            if all_good:
                print("\n🎉 All tables verified successfully!")
            else:
                print("\n⚠️  Some tables have issues")
                
            return all_good
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main function"""
    print("🗄️  EPV Database Initialization Script")
    print("=" * 40)
    print("This will create all EPV tables and populate them with initial data")
    print("on your production server database.")
    print()
    
    # Confirm before proceeding
    proceed = input("Do you want to proceed? (type 'yes' to continue): ")
    if proceed.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Run init_db
    success = run_init_db()
    
    if success:
        # Verify tables
        verify_tables_created()
        
        print("\n🚀 Your server database is now ready!")
        print("   • All EPV tables created")
        print("   • Initial data populated")
        print("   • Ready for production use")
        
    else:
        print("\n❌ Database initialization failed!")
        print("   Check the error messages above for details")

if __name__ == "__main__":
    main()
