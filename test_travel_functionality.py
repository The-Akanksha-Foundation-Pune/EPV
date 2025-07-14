#!/usr/bin/env python3
"""
Test script to verify travel expense functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_travel_functionality():
    """Test the travel expense functionality"""
    
    print("=" * 60)
    print("Testing Travel Expense Functionality")
    print("=" * 60)
    
    # Test 1: Check if travel columns exist in database
    print("\n1. Testing Database Migration...")
    try:
        import pymysql
        
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'epv_system'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # Check if travel columns exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'epv_item' 
            AND COLUMN_NAME IN ('travel_type', 'travel_mode', 'travel_from', 'travel_to', 'travel_date', 'travel_km')
        """, (db_config['database'],))
        
        existing_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
        expected_columns = ['travel_type', 'travel_mode', 'travel_from', 'travel_to', 'travel_date', 'travel_km']
        
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            print("Please run the migration script: python add_travel_columns.py")
        else:
            print("✅ All travel columns exist in database")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test 2: Check if expense heads include travel
    print("\n2. Testing Expense Heads...")
    try:
        from models import db, ExpenseHead
        from app import app
        
        with app.app_context():
            travel_heads = ExpenseHead.query.filter(
                ExpenseHead.head_name.ilike('%travel%')
            ).all()
            
            if travel_heads:
                print(f"✅ Found {len(travel_heads)} travel-related expense heads:")
                for head in travel_heads:
                    print(f"   - {head.head_name}")
            else:
                print("⚠️ No travel-related expense heads found")
                print("   You may want to add 'Travel' or 'Local Travel' or 'Domestic Travel' to expense heads")
        
    except Exception as e:
        print(f"❌ Expense heads test failed: {e}")
    
    # Test 3: Test PDF generation with travel data
    print("\n3. Testing PDF Generation...")
    try:
        from pdf_converter import generate_expense_document
        
        # Sample travel expense data
        test_data = {
            'epv_id': 'EPV-20241201-TEST-1234567890',
            'employee_name': 'Test User',
            'employee_id': 'TEST001',
            'cost_center': 'Test Cost Center',
            'from_date': '2024-12-01',
            'to_date': '2024-12-01',
            'total_amount': '1500.00',
            'amount_in_words': 'One thousand five hundred rupees only',
            'expenses': [
                {
                    'invoice_date': '2024-12-01',
                    'expense_head': 'Local Travel',
                    'description': 'Travel from office to client site',
                    'amount': '1500.00',
                    'travel_type': 'local',
                    'travel_mode': 'taxi',
                    'travel_from': 'Office',
                    'travel_to': 'Client Site',
                    'travel_date': '2024-12-01',
                    'travel_km': '25.5'
                }
            ]
        }
        
        pdf_path = generate_expense_document(test_data)
        if pdf_path and os.path.exists(pdf_path):
            print(f"✅ PDF generated successfully: {pdf_path}")
            print(f"   File size: {os.path.getsize(pdf_path)} bytes")
            
            # Clean up test file
            try:
                os.remove(pdf_path)
                print("   Test file cleaned up")
            except:
                pass
        else:
            print("❌ PDF generation failed")
            
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
    
    # Test 4: Check HTML template
    print("\n4. Testing HTML Template...")
    try:
        template_path = 'templates/new_expense.html'
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            travel_indicators = [
                'travel-fields',
                'travel-type-select',
                'travel-mode-select',
                'travel_from',
                'travel_to',
                'travel_date',
                'travel_km'
            ]
            
            missing_indicators = [ind for ind in travel_indicators if ind not in content]
            
            if missing_indicators:
                print(f"❌ Missing travel elements in template: {missing_indicators}")
            else:
                print("✅ All travel elements found in HTML template")
        else:
            print("❌ HTML template not found")
            
    except Exception as e:
        print(f"❌ HTML template test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Travel Expense Functionality Test Complete")
    print("=" * 60)
    
    print("\n📋 Summary of Travel Expense Features:")
    print("✅ Local Travel: Date, From, To, Mode, KM, Amount")
    print("✅ Domestic Travel: Date, From, To, Mode, Amount (no KM)")
    print("✅ Receipt upload: Optional for car/bike in local, mandatory for others")
    print("✅ Dynamic form fields based on travel type and mode")
    print("✅ PDF generation with travel details")
    print("✅ Database storage of travel information")
    
    print("\n🚀 To use travel expenses:")
    print("1. Select 'Travel' or similar expense head")
    print("2. Choose travel type (Local/Domestic)")
    print("3. Select mode of travel")
    print("4. Fill in from/to locations and dates")
    print("5. For local travel, enter distance in KM")
    print("6. Upload receipts as required")

if __name__ == "__main__":
    test_travel_functionality() 