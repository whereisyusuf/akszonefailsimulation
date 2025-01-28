import mysql.connector
from mysql.connector import Error

# Database connection parameters
HOST = "<mysql-server-name>.mysql.database.azure.com"
USER = "<db server username>"
PASSWORD = "<db server password>"
DATABASE = "<database name>"

# SQL statements
CREATE_DATABASE_QUERY = f"CREATE DATABASE IF NOT EXISTS {DATABASE};"

USE_DATABASE_QUERY = f"USE {DATABASE};"

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    department VARCHAR(255),
    joining_date DATE
);
"""

INSERT_DATA_QUERY = """
INSERT INTO employees (name, age, department, joining_date)
VALUES (%s, %s, %s, %s);
"""

DATA_TO_INSERT = [
    ("Alice", 30, "Engineering", "2023-01-15"),
    ("Bob", 25, "Marketing", "2023-03-22"),
    ("Charlie", 35, "HR", "2023-06-10"),
]

try:
    # Connect to MySQL server
    connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD
    )

    if connection.is_connected():
        print("Connected to MySQL server")

        # Create a cursor object
        cursor = connection.cursor()

        # Create database
        cursor.execute(CREATE_DATABASE_QUERY)
        print(f"Database '{DATABASE}' created or already exists.")

        # Select the database
        cursor.execute(USE_DATABASE_QUERY)
        print(f"Using database '{DATABASE}'.")

        # Create table
        cursor.execute(CREATE_TABLE_QUERY)
        print("Table 'employees' created successfully.")

        # Insert data
        cursor.executemany(INSERT_DATA_QUERY, DATA_TO_INSERT)
        connection.commit()
        print(f"{cursor.rowcount} rows inserted successfully.")

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
