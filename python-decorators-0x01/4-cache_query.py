#!/usr/bin/env python3
import time
import sqlite3
import functools

# Global query cache
query_cache = {}


def with_db_connection(func):
    """Decorator to automatically handle opening and closing the database connection."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def cache_query(func):
    """Decorator to cache query results to avoid redundant database calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the SQL query string from args or kwargs
        query = kwargs.get("query") if "query" in kwargs else (args[1] if len(args) > 1 else None)
        if query in query_cache:
            print(f"[CACHE] Returning cached result for query: {query}")
            return query_cache[query]
        # Execute the query and cache the result
        result = func(*args, **kwargs)
        query_cache[query] = result
        print(f"[CACHE] Stored result for query: {query}")
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")

    # Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")

    print(users_again)
