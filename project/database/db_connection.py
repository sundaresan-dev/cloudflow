import mysql.connector
from mysql.connector import Error
from config import Config
import os

class DatabaseConnection:
    """Database Connection Manager"""
    
    @staticmethod
    def get_connection():
        """Establish MySQL connection"""
        try:
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    @staticmethod
    def initialize_database():
        """Create database and tables if they don't exist"""
        try:
            # Connect without database name first
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                port=Config.DB_PORT
            )
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            print(f"Database '{Config.DB_NAME}' ready.")
            
            # Connect to the database
            connection.database = Config.DB_NAME
            
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            
            # Create tickets table
            create_tickets_table = """
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                subject VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_tickets_table)
            
            # Create deployments table
            create_deployments_table = """
            CREATE TABLE IF NOT EXISTS deployments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                website_type VARCHAR(50) NOT NULL,
                site_folder VARCHAR(255) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_deployments_table)
            
            connection.commit()
            print("Database tables initialized successfully!")
            cursor.close()
            connection.close()
            
        except Error as e:
            print(f"Error initializing database: {e}")

    @staticmethod
    def execute_query(query, params=None, fetch_one=False):
        """Execute a query and return results"""
        connection = DatabaseConnection.get_connection()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            connection.commit()
            cursor.close()
            return result
            
        except Error as e:
            print(f"Query execution error: {e}")
            return None
        finally:
            if connection.is_connected():
                connection.close()

    @staticmethod
    def execute_update(query, params=None):
        """Execute INSERT, UPDATE, or DELETE query"""
        connection = DatabaseConnection.get_connection()
        if connection is None:
            return False
        
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
            
        except Error as e:
            print(f"Update execution error: {e}")
            return False
        finally:
            if connection.is_connected():
                connection.close()

    @staticmethod
    def import_sql_file(sql_file_path, db_name):
        """Import SQL file into database"""
        try:
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=db_name,
                port=Config.DB_PORT
            )
            cursor = connection.cursor()
            
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                
            # Split statements and execute
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            connection.commit()
            print(f"SQL file imported successfully: {sql_file_path}")
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            print(f"Error importing SQL file: {e}")
            return False
