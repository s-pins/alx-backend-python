#!/usr/bin/python3
import seed


def stream_user_ages():
    """Generator that yields ages one by one from the user_data table."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:
        yield row["age"]

    connection.close()


def calculate_average_age():
    """Compute average user age using the generator."""
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count > 0:
        avg = total_age / count
        print(f"Average age of users: {avg:.2f}")
    else:
        print("No users found.")


if __name__ == "__main__":
    calculate_average_age()
