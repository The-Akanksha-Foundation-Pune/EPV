import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Motoming@123',
    'db': 'AFDW',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def add_epv_approval_table():
    """Create the EPVApproval table."""
    try:
        # Connect to the database
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # Check if the table already exists
            cursor.execute("SHOW TABLES LIKE 'epv_approval'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                # Create the table
                sql = """
                CREATE TABLE epv_approval (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    epv_id INT NOT NULL,
                    approver_email VARCHAR(100) NOT NULL,
                    approver_name VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    action_date DATETIME,
                    comments TEXT,
                    token VARCHAR(100) UNIQUE,
                    FOREIGN KEY (epv_id) REFERENCES epv(id)
                )
                """
                cursor.execute(sql)
                connection.commit()
                print("Successfully created 'epv_approval' table.")
            else:
                print("Table 'epv_approval' already exists.")
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
    finally:
        connection.close()

if __name__ == "__main__":
    add_epv_approval_table()
