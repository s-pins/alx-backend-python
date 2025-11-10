#!/usr/bin/env python3
import sqlite3


class DatabaseConnection:
    """Custom class-based context manager for handling SQLite database connections."""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Establish the database connection and return the connection object."""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the connection is closed, even if an exception occurs."""
        if self.conn:
            self.conn.close()
        # Returning False means exceptions (if any) are propagated
        return False


if __name__ == "__main__":
    # Using the custom context manager to perform a database query
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
