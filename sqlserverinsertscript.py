import pyodbc # pip install pyodbc

# Azure SQL Managed Instance connection details
server = "<sqlmi-server-name>"  # Replace with your server name
database = "<db name>"  # Replace with your database name
username = "<db server user name>"  # Replace with your username
password = "<db server password>"  # Replace with your password

# Connection string
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# SQL commands
create_schema_query = "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'SalesLT') BEGIN EXEC('CREATE SCHEMA SalesLT'); END"

create_table_query = """
CREATE TABLE [SalesLT].[Address] (
    AddressID INT IDENTITY(1,1) PRIMARY KEY,
    AddressLine1 NVARCHAR(100) NOT NULL,
    City NVARCHAR(50) NOT NULL,
    StateProvince NVARCHAR(50) NOT NULL,
    PostalCode NVARCHAR(20) NOT NULL,
    CountryRegion NVARCHAR(50) NOT NULL
);
"""

insert_data_query = """
INSERT INTO [SalesLT].[Address] (AddressLine1, City, StateProvince, PostalCode, CountryRegion)
VALUES (?, ?, ?, ?, ?);
"""

sample_data = [
    ("123 Elm St", "Seattle", "WA", "98101", "USA"),
    ("456 Pine St", "Portland", "OR", "97201", "USA"),
    ("789 Oak St", "San Francisco", "CA", "94102", "USA"),
    ("101 Maple Ave", "Denver", "CO", "80201", "USA"),
    ("202 Birch Rd", "Chicago", "IL", "60601", "USA"),
    ("303 Cedar Dr", "Austin", "TX", "73301", "USA"),
    ("404 Spruce Ln", "Phoenix", "AZ", "85001", "USA"),
    ("505 Walnut St", "Boston", "MA", "02101", "USA"),
    ("606 Chestnut Blvd", "Miami", "FL", "33101", "USA"),
    ("707 Willow Way", "New York", "NY", "10001", "USA"),
]

try:
    # Connect to the database
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        print("Connected to the database.")

        # Create schema if it doesn't exist
        try:
            cursor.execute(create_schema_query)
            print("Schema [SalesLT] ensured to exist.")
        except pyodbc.Error as e:
            print(f"Schema creation failed: {e}")

        # Create table
        try:
            cursor.execute(create_table_query)
            print("Table [SalesLT].[Address] created successfully.")
        except pyodbc.Error as e:
            print(f"Table creation failed: {e}")

        # Insert data
        try:
            cursor.executemany(insert_data_query, sample_data)
            conn.commit()
            print("Sample data inserted successfully.")
        except pyodbc.Error as e:
            print(f"Data insertion failed: {e}")

except pyodbc.Error as e:
    print(f"Database connection failed: {e}")
