import os

dbname = os.getenv("DB_NAME", "postgres")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", 5432)
