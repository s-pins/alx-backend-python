# Python Generators — Task 0: Getting Started

**Project:** ALX Backend Python  
**Directory:** `python-generators-0x00`  
**Task:** 0. Getting started with Python generators  
**Author:** Frank Wambua  
**Date:** October 2025  

---

## 🎯 Objective
Create a Python script (`seed.py`) that sets up a MySQL database named **`ALX_prodev`**, defines the **`user_data`** table, and populates it using data from a CSV file.  
This serves as the foundation for later tasks involving generator functions that stream database rows efficiently.

---

## 🧱 Database Schema

**Database:** `ALX_prodev`  
**Table:** `user_data`

| Field      | Type        | Constraints                      |
|-------------|-------------|----------------------------------|
| `user_id`   | CHAR(36)    | Primary Key (UUID) + Indexed     |
| `name`      | VARCHAR(255)| NOT NULL                         |
| `email`     | VARCHAR(255)| NOT NULL                         |
| `age`       | DECIMAL(3,0)| NOT NULL                         |

---

## 🧩 Script Details

**File:** `seed.py`

### Functions

| Function | Description |
|-----------|-------------|
| `connect_db()` | Connects to the MySQL server (no database selected). |
| `create_database(connection)` | Creates `ALX_prodev` if it does not exist. |
| `connect_to_prodev()` | Connects to the `ALX_prodev` database. |
| `create_table(connection)` | Creates the `user_data` table if missing. |
| `insert_data(connection, data)` | Reads `user_data.csv` and inserts rows with unique UUIDs. |

---

## 🧰 Setup Instructions

### 1️⃣ Prerequisites
- **Python 3.x**
- **MySQL Server** running locally
- **mysql-connector-python** package  
  ```bash
  pip install mysql-connector-python
