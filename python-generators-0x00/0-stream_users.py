#!/usr/bin/python3
"""
Streams rows from the user_data table using a Python generator.
"""

import mysql.connector


def stream_users():
    """
    Generator function that yields one user record at a time
    from the user_data table in the ALX_prodev database.
    """
    try:
        # connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data;")

        # yield one row at a time
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        # close resources safely
        if cursor:
            cursor.close()
        if connection:
            connection.close()
