import mysql.connector
import pickle
import numpy as np
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Update these credentials with your MySQL settings
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root1234', # Default XAMPP/WAMP is often empty
            'database': 'face_attendance_db'
        }
        self.setup_database()

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def setup_database(self):
        try:
            # Connect without database first to create it
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            conn.close()

            # Connect to the database to create/update tables
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create basic tables if they don't exist
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY)")
            cursor.execute("CREATE TABLE IF NOT EXISTS attendance (id INT AUTO_INCREMENT PRIMARY KEY)")

            # Auto-Add missing columns to 'users' table
            columns_users = {
                'user_id': "VARCHAR(50) UNIQUE AFTER id",
                'name': "VARCHAR(255) AFTER user_id",
                'encoding': "LONGBLOB AFTER name"
            }
            for col, spec in columns_users.items():
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {spec}")
                except:
                    pass # Column likely already exists

            # Auto-Add missing columns to 'attendance' table
            columns_attendance = {
                'user_id': "VARCHAR(50) AFTER id",
                'name': "VARCHAR(255) AFTER user_id",
                'time': "DATETIME AFTER name",
                'action': "VARCHAR(10) AFTER time"
            }
            for col, spec in columns_attendance.items():
                try:
                    cursor.execute(f"ALTER TABLE attendance ADD COLUMN {col} {spec}")
                except:
                    pass # Column likely already exists

            conn.commit()
            conn.close()
            print("MySQL Database and Tables synchronized successfully.")
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")

    def register_user(self, user_id, name, encoding):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Convert numpy array to binary for storage
        encoding_bin = pickle.dumps(encoding)
        print(f"DEBUG: Saving user '{name}' (ID: {user_id}) to MySQL. Encoding size: {len(encoding_bin)} bytes.")
        try:
            cursor.execute("INSERT INTO users (user_id, name, encoding) VALUES (%s, %s, %s)", (user_id, name, encoding_bin))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Registration Error: {err}")
            return False
        finally:
            conn.close()


    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, encoding FROM users")
            results = cursor.fetchall()
            print(f"DEBUG: Fetched {len(results)} users from MySQL.")
            # Convert binary back to numpy arrays
            users = []
            for user_id, name, enc_bin in results:
                users.append({'user_id': user_id, 'name': name, 'encoding': pickle.loads(enc_bin)})
            conn.close()
            return users

        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def log_attendance(self, user_id, name, action):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("INSERT INTO attendance (user_id, name, time, action) VALUES (%s, %s, %s, %s)", (user_id, name, now, action))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging attendance: {e}")
            return False

