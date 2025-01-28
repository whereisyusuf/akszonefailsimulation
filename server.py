from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# FastAPI app
app = FastAPI()

# MySQL connection string
MYSQL_DATABASE_URL = "<my-sql-connection-string>"
mysql_engine = create_engine(MYSQL_DATABASE_URL)
MySQLSession = sessionmaker(bind=mysql_engine)

# SQL Server connection string
SQLSERVER_DATABASE_URL = "<sql-server-connection-string>"
sqlserver_engine = create_engine(SQLSERVER_DATABASE_URL)
SQLServerSession = sessionmaker(bind=sqlserver_engine)

@app.get("/mysql-data")
def get_mysql_data():
    try:
        session = MySQLSession()
        query = text("SELECT * FROM employees LIMIT 10")
        result = session.execute(query).fetchall()
        session.close()
        
        # Convert rows to dictionaries
        data = [dict(row._mapping) for row in result]
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sqlserver-data")
def get_sqlserver_data():
    try:
        session = SQLServerSession()
        query = text("SELECT TOP 10 * FROM [SalesLT].[Address]")
        result = session.execute(query).fetchall()
        session.close()

        # Convert rows to dictionaries
        data = [dict(row._mapping) for row in result]

        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
