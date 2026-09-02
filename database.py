import mysql.connector
import random
import string
import os


DB_HOST = os.getenv("MYSQLHOST", "localhost")
DB_PORT = int(os.getenv("MYSQLPORT", "3306"))
DB_USER = os.getenv("MYSQLUSER", "root")
DB_PASSWORD = os.getenv("MYSQLPASSWORD", "root")
DB_NAME = os.getenv("MYSQLDATABASE", "expense_tracker")


def create_database():
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
    )

    cursor.close()
    connection.close()


def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    return connection



# -------------------------
# Trips
# -------------------------

def create_trips_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


def add_trip(name):
    connection = get_db_connection()
    cursor = connection.cursor()

    while True:
        trip_code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        cursor.execute(
            "SELECT id FROM trips WHERE trip_code = %s",
            (trip_code,)
        )

        if cursor.fetchone() is None:
            break

    cursor.execute(
        """
        INSERT INTO trips (name, trip_code)
        VALUES (%s, %s)
        """,
        (name, trip_code)
    )

    connection.commit()

    trip_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return trip_id


def get_trips():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM trips ORDER BY id DESC"
    )

    trips = cursor.fetchall()

    cursor.close()
    connection.close()

    return trips


def get_trip(trip_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM trips WHERE id = %s",
        (trip_id,)
    )

    trip = cursor.fetchone()

    cursor.close()
    connection.close()

    return trip

def complete_trip(trip_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE trips
        SET status = 'completed'
        WHERE id = %s
    """, (trip_id,))

    connection.commit()

    cursor.close()
    connection.close()

def get_trip_by_code(trip_code):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM trips
        WHERE trip_code = %s
    """, (trip_code,))

    trip = cursor.fetchone()

    cursor.close()
    connection.close()

    return trip

def join_trip(trip_id, member_name):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO members (trip_id, name)
        VALUES (%s, %s)
    """, (trip_id, member_name))

    connection.commit()

    member_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return member_id
# -------------------------
# Members
# -------------------------

def create_members_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            trip_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


def add_member(trip_id, name):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO members (trip_id, name)
        VALUES (%s, %s)
        """,
        (trip_id, name)
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_members(trip_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM members
        WHERE trip_id = %s
        ORDER BY id ASC
        """,
        (trip_id,)
    )

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return members

def delete_member(member_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM members
        WHERE id = %s
        """,
        (member_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()


# -------------------------
# Expenses
# -------------------------

def create_expenses_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            trip_id INT NOT NULL,
            title VARCHAR(100) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            paid_by INT NOT NULL,
            expense_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id),
            FOREIGN KEY (paid_by) REFERENCES members(id)
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

def create_expense_participants_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_participants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            expense_id INT NOT NULL,
            member_id INT NOT NULL,
            share_amount DECIMAL(10, 2) NOT NULL,

            FOREIGN KEY (expense_id)
                REFERENCES expenses(id)
                ON DELETE CASCADE,

            FOREIGN KEY (member_id)
                REFERENCES members(id)
                ON DELETE CASCADE,

            UNIQUE (expense_id, member_id)
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()

def add_expense_participant(expense_id, member_id, share_amount):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO expense_participants
        (expense_id, member_id, share_amount)
        VALUES (%s, %s, %s)
        """,
        (expense_id, member_id, share_amount)
    )

    connection.commit()

    cursor.close()
    connection.close()

def get_expense_participants(expense_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            expense_participants.member_id,
            members.name
        FROM expense_participants
        JOIN members
            ON expense_participants.member_id = members.id
        WHERE expense_participants.expense_id = %s
        """,
        (expense_id,)
    )

    participants = cursor.fetchall()

    cursor.close()
    connection.close()

    return participants

def add_expense(trip_id, title, amount, paid_by, expense_date):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (trip_id, title, amount, paid_by, expense_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        trip_id,
        title,
        amount,
        paid_by,
        expense_date
    ))

    connection.commit()

    expense_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return expense_id

def get_expenses(trip_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            expenses.*,
            members.name AS paid_by_name
        FROM expenses
        JOIN members
            ON expenses.paid_by = members.id
        WHERE expenses.trip_id = %s
        ORDER BY expenses.expense_date DESC, expenses.id DESC
        """,
        (trip_id,)
    )

    expenses = cursor.fetchall()

    cursor.close()
    connection.close()

    return expenses

def get_balances(trip_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            members.id,
            members.name,

            COALESCE(
                (
                    SELECT SUM(expenses.amount)
                    FROM expenses
                    WHERE expenses.trip_id = %s
                    AND expenses.paid_by = members.id
                ),
                0
            ) AS total_paid,

            COALESCE(
                (
                    SELECT SUM(expense_participants.share_amount)
                    FROM expense_participants
                    JOIN expenses
                        ON expense_participants.expense_id = expenses.id
                    WHERE expenses.trip_id = %s
                    AND expense_participants.member_id = members.id
                ),
                0
            ) AS total_share

        FROM members
        WHERE members.trip_id = %s
        ORDER BY members.id ASC
        """,
        (trip_id, trip_id, trip_id)
    )

    balances = cursor.fetchall()

    for balance in balances:

        balance["balance"] = (
            balance["total_paid"]
            - balance["total_share"]
        )

    cursor.close()
    connection.close()

    return balances

def get_split_totals(trip_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            members.id,
            members.name,
            COALESCE(
                SUM(expense_participants.share_amount),
                0
            ) AS total_share
        FROM members
        LEFT JOIN expense_participants
            ON members.id = expense_participants.member_id
        LEFT JOIN expenses
            ON expense_participants.expense_id = expenses.id
            AND expenses.trip_id = %s
        WHERE members.trip_id = %s
        GROUP BY members.id, members.name
        ORDER BY members.id ASC
        """,
        (trip_id, trip_id)
    )

    split_totals = cursor.fetchall()

    cursor.close()
    connection.close()

    return split_totals

def get_total_paid(trip_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            members.id,
            members.name,
            COALESCE(
                SUM(expenses.amount),
                0
            ) AS total_paid
        FROM members
        LEFT JOIN expenses
            ON members.id = expenses.paid_by
            AND expenses.trip_id = %s
        WHERE members.trip_id = %s
        GROUP BY members.id, members.name
        ORDER BY members.id ASC
        """,
        (trip_id, trip_id)
    )

    total_paid = cursor.fetchall()

    cursor.close()
    connection.close()

    return total_paid