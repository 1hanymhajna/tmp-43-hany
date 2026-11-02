import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def connect_to_postgres():
    try:
        con = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        return con
    except psycopg2.Error as e:
        print(f"Error connecting to Postgres: {e}")

def create_schema(schema_name,con):
    try:
        cur = con.cursor()
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        cur.close()
        con.commit()
        print(f"Schema {schema_name} created successfully")
    except psycopg2.Error as e:
        print(f"Error creating schema {schema_name}: {e}")
        con.rollback()
        return False
    return True


sound_table_create_query = """
CREATE TABLE IF NOT EXISTS sounds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

def create_table(table_name,con):
    try:
        cur = con.cursor()
        cur.execute(sound_table_create_query)
        cur.close()
        con.commit()
        print(f"Table {table_name} created successfully")
    except psycopg2.Error as e:
        print(f"Error creating table {table_name}: {e}")
        con.rollback()
        return False
    return True


insert_data_query = """
INSERT INTO sounds (name, description) VALUES (%s, %s)
"""
def insert_data(data,con):
    try:
        cur = con.cursor()
        ## we got error that dict is not  a sequence so we need to convert it to a tuple
        data = tuple(data.values())
        cur.execute(insert_data_query, data)
        cur.close()
        con.commit()
        print(f"Data inserted successfully")
    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")
        con.rollback()
        return False
    return True

read_data_query = """
SELECT * FROM sounds
"""
def read_data(con):
    try:
        cur = con.cursor()
        cur.execute(read_data_query)
        data = cur.fetchall()
        cur.close()
        return data
    except psycopg2.Error as e:
        print(f"Error reading data: {e}")
        return False

