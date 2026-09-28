import sqlite3
import os
import sys


# --------------------------------------------------
# Application Root
# --------------------------------------------------

if getattr(
    sys,
    "frozen",
    False
):

    # Packaged .exe
    #
    # Example:
    # dist/
    # ├── AI Email Agent/
    # ├── AI Email Agent Monitor/
    # └── email_agent.db
    #
    # Application root = dist/

    PROJECT_FOLDER = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                sys.executable
            )
        )
    )

else:

    # Normal Python execution

    PROJECT_FOLDER = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                __file__
            )
        )
    )


# --------------------------------------------------
# Database File
# --------------------------------------------------

DATABASE_FILE = os.path.join(
    PROJECT_FOLDER,
    "email_agent.db"
)


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    return connection


# --------------------------------------------------
# Create Tables
# --------------------------------------------------

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            invoice_number TEXT,

            vendor TEXT,

            invoice_date TEXT,

            due_date TEXT,

            total_amount TEXT,

            currency TEXT,

            filename TEXT,

            email_id TEXT,

            drive_link TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()


# --------------------------------------------------
# Save Invoice
# --------------------------------------------------

def save_invoice(
    invoice_number,
    vendor,
    invoice_date,
    due_date,
    total_amount,
    currency,
    filename,
    email_id,
    drive_link
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO invoices (

            invoice_number,
            vendor,
            invoice_date,
            due_date,
            total_amount,
            currency,
            filename,
            email_id,
            drive_link

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            invoice_number,
            vendor,
            invoice_date,
            due_date,
            total_amount,
            currency,
            filename,
            email_id,
            drive_link
        )
    )

    connection.commit()

    connection.close()


# --------------------------------------------------
# Test Database
# --------------------------------------------------

if __name__ == "__main__":

    create_tables()

    print(
        "Database created successfully."
    )

    print(
        "Database location:"
    )

    print(
        DATABASE_FILE
    )