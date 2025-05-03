import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

import mysql.connector
from config.settings import DB_CONFIG
from services.fee_tracking import detect_pending_fees
from services.reminder_scheduler import schedule_reminders
from services.notification import send_email_notification, send_sms_notification
from models.fee_record import FeeRecord
from utils.helper import format_due_date
from datetime import datetime

def create_fees_table():
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    cursor = connection.cursor()

    # Create the fees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            parent_name VARCHAR(255) NOT NULL,
            amount_due DECIMAL(10, 2) NOT NULL,
            due_date DATE NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'Pending'
        )
    ''')

    # Commit changes and close the connection
    connection.commit()
    connection.close()

def update_fees_table():
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    cursor = connection.cursor()

    # Check if columns already exist before adding them
    cursor.execute("SHOW COLUMNS FROM fees LIKE 'parent_email'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE fees ADD COLUMN parent_email VARCHAR(255)")

    cursor.execute("SHOW COLUMNS FROM fees LIKE 'parent_phone'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE fees ADD COLUMN parent_phone VARCHAR(15)")

    cursor.execute("SHOW COLUMNS FROM fees LIKE 'remaining_balance'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE fees ADD COLUMN remaining_balance DECIMAL(10, 2) DEFAULT 0.00")

    # Commit changes and close the connection
    connection.commit()
    connection.close()

def insert_sample_data():
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    cursor = connection.cursor()

    # Insert sample data into the fees table
    cursor.executemany('''
        INSERT INTO fees (student_name, parent_name, amount_due, due_date, parent_email, parent_phone, remaining_balance)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', [
        ("Rohan", "Mr. Kumar", 8000, "2025-05-10", "kumar.parent@example.com", "+1234567890", 8000),
        ("Ananya", "Mrs. Sharma", 5000, "2025-05-05", "sharma.parent@example.com", "+9876543210", 5000)
    ])

    # Commit changes and close the connection
    connection.commit()
    connection.close()

def update_parent_email():
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    cursor = connection.cursor()

    # Update the parent email for Rohan
    cursor.execute('''
        UPDATE fees
        SET parent_email = %s
        WHERE student_name = %s
    ''', ("nithingowdabk2003@gmail.com", "Rohan"))

    # Commit changes and close the connection
    connection.commit()
    connection.close()

# Update FeeRecord instances to include parent_email
fee_records = [
    FeeRecord("Rohan", "Mr. Kumar", 8000, datetime(2025, 5, 10).date(), "nithingowdabk2003@gmail.com"),
    FeeRecord("Ananya", "Mrs. Sharma", 5000, datetime(2025, 5, 5).date(), "sharma.parent@example.com")
]

# Detect pending fees
pending_fees = detect_pending_fees(fee_records)

# Use the actual parent email from the FeeRecord object
for record, urgency in pending_fees:
    reminders = schedule_reminders(record, payment_behavior="on-time")
    if reminders:  # Only send a single reminder
        reminder_date, reminder_type = reminders[0]
        message = f"Dear {record.parent_name}, your child {record.student_name}'s fee of ₹{record.amount_due} is due on {format_due_date(record.due_date)}."
        try:
            send_email_notification(record.parent_email, reminder_type, message)
            print(f"Email sent to {record.parent_email}")
        except Exception as e:
            print(f"Failed to send email to {record.parent_email}")

if __name__ == "__main__":
    create_fees_table()
    update_fees_table()
    insert_sample_data()
    update_parent_email()