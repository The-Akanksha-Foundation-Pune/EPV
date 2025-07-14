#!/usr/bin/env python3
"""
Database migration script to add travel expense fields to epv_item table
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_travel_columns():
    """Add travel expense columns to epv_item table"""
    
    # Database connection parameters
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'epv_system'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        # Connect to database
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("Connected to database successfully")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'epv_item' 
            AND COLUMN_NAME IN ('travel_type', 'travel_mode', 'travel_from', 'travel_to', 'travel_date', 'travel_km')
        """, (db_config['database'],))
        
        existing_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
        print(f"Existing travel columns: {existing_columns}")
        
        # Add columns that don't exist
        columns_to_add = [
            ('travel_type', 'VARCHAR(20) NULL COMMENT "local, domestic"'),
            ('travel_mode', 'VARCHAR(50) NULL COMMENT "car, bike, bus, train, flight, taxi, auto, other"'),
            ('travel_from', 'VARCHAR(100) NULL COMMENT "Source location"'),
            ('travel_to', 'VARCHAR(100) NULL COMMENT "Destination location"'),
            ('travel_date', 'DATE NULL COMMENT "Travel date"'),
            ('travel_km', 'FLOAT NULL COMMENT "Distance in kilometers for local travel"')
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE epv_item ADD COLUMN {column_name} {column_def}"
                    print(f"Executing: {sql}")
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"⏭️ Column {column_name} already exists, skipping")
        
        # Commit changes
        connection.commit()
        print("✅ Migration completed successfully")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("EPV System - Travel Expense Migration")
    print("=" * 60)
    add_travel_columns()
    print("=" * 60) 