import sys
import os

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection
import mysql.connector
from config import Config

def update_schema():
    print("Updating database schema...")
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = connection.cursor()
        
        # Add is_admin column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            print("Added is_admin to users table.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # Duplicate column name
                print("is_admin column already exists.")
            else:
                print(f"Error adding column: {err}")
                
        # Make the test user an admin for easy testing
        cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = 'test@example.com'")
        print("Set test@example.com as an admin.")

        # Create tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                subject VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("Created tickets table.")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Schema update complete.")
        
    except Exception as e:
        print(f"Failed to update schema: {e}")

if __name__ == '__main__':
    update_schema()
