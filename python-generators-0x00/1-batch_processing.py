#!/usr/bin/python3
"""
Fetches user data in batches using generators and filters users over age 25.
"""

import mysql.connector


def stream_users_in_batches(batch_size):
    """
    Generator that yields users in batches of `batch_size` from user_data table.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # update if needed
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data;")

        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over age 25.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                print(user)
