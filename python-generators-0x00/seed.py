#!/usr/bin/python3
"""
seed.py — Setup script for ALX_prodev database and user_data table.
"""

import csv
import uuid
import mysql.connector
from mysql.connector import errorcode


def connect_db():
    """Connect to the MySQL server (no specific database)."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def create_database(connection):
    """Create the ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("Database ALX_prodev created or already exists.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


def connect_to_prodev():
    """Connect directly to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


def create_table(connection):
    """Create user_data table if it does not exist."""
    table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(3,0) NOT NULL,
        INDEX(email)
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(table_query)
        connection.commit()
        print("Table user_data created successfully.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")


def insert_data(connection, csv_file):
    """Insert data from CSV file into user_data table."""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name'].strip()
                email = row['email'].strip()
                age = int(float(row['age']))
                user_id = str(uuid.uuid4())

                # Skip duplicate email entries
                cursor.execute("SELECT email FROM user_data WHERE email = %s;", (email,))
                if cursor.fetchone():
                    continue

                cursor.execute(
                    "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s);",
                    (user_id, name, email, age)
                )

        connection.commit()
        cursor.close()
        print("Data inserted successfully from CSV.")
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        print("Connection successful.")

        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_data LIMIT 5;")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            cursor.close()
            connection.close()
