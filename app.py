# Standard library imports
import os
from datetime import datetime

# Third-party imports
from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape  # Import landscape
from reportlab.pdfgen import canvas
import mysql.connector

# Local imports
from TeacherPerformanceAI import main as teacher_performance_logic
from services.reminder_scheduler import schedule_reminders
from services.notification import send_email_notification  # Added import
from models.fee_record import FeeRecord
from config.settings import DB_CONFIG

# Determine the absolute path to the public folder
project_root = os.path.dirname(os.path.abspath(__file__))
# Change build_folder to public_folder
public_folder = os.path.join(project_root, 'public')

# Initialize Flask app
# Point static_folder to the 'public' directory using an absolute path
app = Flask(__name__, static_folder=public_folder, static_url_path='')  # Use absolute path for static_folder
CORS(app)

# Serve static files from the 'public' directory
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the static files from the public directory."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        # If the path points to an existing file in the static folder, serve it.
        return send_from_directory(app.static_folder, path)
    else:
        # Otherwise, serve the main index.html file.
        return send_from_directory(app.static_folder, 'index.html')

# API Endpoints

@app.route('/api/teacher-performance', methods=['GET'])
def teacher_performance():
    """Endpoint to fetch teacher performance data from the database and provide a PDF download link."""
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    cursor = connection.cursor(dictionary=True)

    # Fetch teacher performance data
    print("Executing query to fetch teacher performance data...")
    cursor.execute("SELECT teacher_name AS name, feedback_score, attendance_percentage, result_percentage, activity_score, final_score, rating, ai_suggestion FROM teacher_performance")
    teacher_data = cursor.fetchall()
    print("Query executed successfully. Fetched data:", teacher_data)

    # Close the database connection
    cursor.close()
    connection.close()

    # Generate PDF
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))  # Use landscape orientation
    page_width, page_height = landscape(letter)  # Get dimensions

    title_y = page_height - 50
    header_y = title_y - 30
    line_y = header_y - 10
    data_start_y = line_y - 20

    pdf.drawString(50, title_y, "Teacher Performance Report")

    # Define column x-coordinates
    col_x = {
        "name": 50,
        "feedback": 150,
        "attendance": 250,
        "result": 350,
        "activity": 450,
        "final": 550,
        "rating": 650,
        "suggestion": 700  # Adjusted for landscape
    }
    line_end_x = page_width - 50  # Adjust line end

    # Function to draw headers (to avoid repetition in pagination)
    def draw_headers(y_pos):
        pdf.drawString(col_x["name"], y_pos, "Name")
        pdf.drawString(col_x["feedback"], y_pos, "Feedback Score")
        pdf.drawString(col_x["attendance"], y_pos, "Attendance %")
        pdf.drawString(col_x["result"], y_pos, "Result %")
        pdf.drawString(col_x["activity"], y_pos, "Activity Score")
        pdf.drawString(col_x["final"], y_pos, "Final Score")
        pdf.drawString(col_x["rating"], y_pos, "Rating")
        pdf.drawString(col_x["suggestion"], y_pos, "AI Suggestion")
        pdf.line(col_x["name"], y_pos - 10, line_end_x, y_pos - 10)  # Draw line below headers

    # Draw initial headers
    draw_headers(header_y)
    y_position = data_start_y

    # Add teacher performance data to the PDF
    for teacher in teacher_data:
        if y_position < 50:  # Check if the y_position is too low for the current page
            pdf.showPage()  # Create a new page
            # Reset y_position and redraw headers for the new page
            header_y_new_page = page_height - 50  # Position headers near top
            draw_headers(header_y_new_page)
            y_position = header_y_new_page - 20  # Start data below new headers

        pdf.drawString(col_x["name"], y_position, teacher['name'])
        pdf.drawString(col_x["feedback"], y_position, str(teacher['feedback_score']))
        pdf.drawString(col_x["attendance"], y_position, str(teacher['attendance_percentage']))
        pdf.drawString(col_x["result"], y_position, str(teacher['result_percentage']))
        pdf.drawString(col_x["activity"], y_position, str(teacher['activity_score']))
        pdf.drawString(col_x["final"], y_position, str(teacher['final_score']))
        pdf.drawString(col_x["rating"], y_position, teacher['rating'])
        # Handle potential long suggestions (simple wrap example)
        suggestion_text = teacher['ai_suggestion'] if teacher['ai_suggestion'] else ""
        max_suggestion_width = line_end_x - col_x["suggestion"]
        # Basic text wrapping (can be improved with reportlab's Paragraph)
        if pdf.stringWidth(suggestion_text, pdf._fontname, pdf._fontsize) > max_suggestion_width:
            # Simple split for demonstration, might need better logic
            suggestion_lines = [suggestion_text[i:i+40] for i in range(0, len(suggestion_text), 40)]  # Approx 40 chars
            line_offset = 0
            for line in suggestion_lines:
                pdf.drawString(col_x["suggestion"], y_position - line_offset, line)
                line_offset += 12  # Move down for next line
            y_position -= (len(suggestion_lines) - 1) * 12  # Adjust main y_position based on wrapped lines
        else:
            pdf.drawString(col_x["suggestion"], y_position, suggestion_text)

        y_position -= 20  # Move to next row position

    # Save the PDF
    pdf.save()
    pdf_buffer.seek(0)

    # Save the PDF to a file (optional, for persistent storage)
    pdf_path = os.path.join(app.static_folder, "teacher_performance.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_buffer.getvalue())

    # Return JSON response with download link
    return jsonify({
        "message": "Teacher performance data processed successfully.",
        "data": teacher_data,
        "pdf_download_link": "/teacher_performance.pdf"
    })

# Renamed from /api/fees-reminder
@app.route('/api/send-all-reminders', methods=['POST'])
def send_all_reminders():
    """Endpoint to fetch all pending fee records and send a reminder email for each."""
    reminders_sent_info = [] # Keep track of sent reminders
    fee_records_from_db = []
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = connection.cursor(dictionary=True)
        print("Executing query to fetch pending fee records for sending...")
        cursor.execute("""
            SELECT student_name, parent_name, amount_due, due_date, parent_email, payment_status
            FROM fees
            WHERE payment_status = 'Pending'
        """)
        fee_records_from_db = cursor.fetchall()
        print(f"Query executed successfully. Fetched {len(fee_records_from_db)} records for sending.")
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": "Database connection or query failed", "details": str(err)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    # Process fetched records and send reminders
    today = datetime.now().date()
    processed_records_count = 0
    reminders_sent_count = 0

    for record_data in fee_records_from_db:
        processed_records_count += 1
        due_date_str = "N/A" # Default in case parsing fails
        if 'due_date' in record_data and record_data['due_date']:
            due_date = record_data['due_date']
            if isinstance(due_date, datetime):
                due_date_obj = due_date.date()
                due_date_str = due_date_obj.strftime('%Y-%m-%d')
            elif isinstance(due_date, str):
                 try:
                     due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date() # Adjust format if needed
                     due_date_str = due_date_obj.strftime('%Y-%m-%d')
                 except ValueError:
                     print(f"Could not parse date string: {record_data['due_date']} for student {record_data['student_name']}")
                     due_date_str = str(record_data['due_date']) # Use original string if parsing fails
            elif hasattr(due_date, 'isoformat'): # Handle date objects
                due_date_obj = due_date
                due_date_str = due_date.isoformat()

        # Construct email
        subject = f"Reminder: Outstanding Fee Payment for {record_data['student_name']}"
        body = (
            f"Dear {record_data['parent_name']},\n\n"
            f"This is a reminder regarding the outstanding fee payment of ${record_data['amount_due']:.2f} "
            f"for {record_data['student_name']}, which was due on {due_date_str}.\n\n"
            f"Please make the payment as soon as possible.\n\n"
            f"Thank you,\nSchool Administration"
        )

        # Send email
        print(f"Attempting to send reminder to {record_data['parent_email']} for student {record_data['student_name']}")
        try:
            send_email_notification(record_data['parent_email'], subject, body)
            reminders_sent_count += 1
            # Record sent info
            reminders_sent_info.append({
                "student_name": record_data['student_name'],
                "parent_email": record_data['parent_email'],
                "due_date": due_date_str,
                "reminder_type": "Outstanding Fee Reminder",
                "sent_date": today.isoformat()
            })
        except Exception as email_err:
             print(f"Failed to send email to {record_data['parent_email']} for student {record_data['student_name']}: {email_err}")
             # Optionally record failed attempts if needed

    return jsonify({
        "message": f"Processed {processed_records_count} pending fee records. Sent {reminders_sent_count} reminders.",
        "reminders_sent_details": reminders_sent_info
    })

@app.route('/api/pending-fees', methods=['GET'])
def get_pending_fees():
    """Endpoint to fetch all pending fee records for display."""
    pending_fees = []
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = connection.cursor(dictionary=True)

        # Fetch all fee records with 'Pending' status, including the fee ID
        print("Executing query to fetch all pending fee records for display...")
        cursor.execute("""
            SELECT id as fee_id, student_name, parent_name, amount_due, due_date, parent_email, payment_status
            FROM fees
            WHERE payment_status = 'Pending'
            ORDER BY due_date ASC
        """)
        pending_fees = cursor.fetchall()
        print(f"Query executed successfully. Fetched {len(pending_fees)} pending records for display.")

        # Convert date objects to strings for JSON serialization
        for record in pending_fees:
            if isinstance(record['due_date'], datetime):
                record['due_date'] = record['due_date'].strftime('%Y-%m-%d')
            elif hasattr(record['due_date'], 'isoformat'): # Handle date objects
                record['due_date'] = record['due_date'].isoformat()

        # Close the database connection
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Database error while fetching pending fees: {err}")
        return jsonify({"error": "Database connection or query failed", "details": str(err)}), 500
    except Exception as e:
        print(f"An unexpected error occurred while fetching pending fees: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    return jsonify(pending_fees)

@app.route('/api/check-db-connection', methods=['GET'])
def check_db_connection():
    """Endpoint to check if the database is connected."""
    try:
        # Attempt to connect to the database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        connection.close()
        return jsonify({"message": "Database connection successful."}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": "Database connection failed", "details": str(err)}), 500

# New endpoint to add a student
@app.route('/api/add-student', methods=['POST'])
def add_student():
    """Endpoint to add a new student and optionally their initial fee record."""
    data = request.get_json()

    # Basic validation for student/parent details
    if not data or not data.get('student_name') or not data.get('parent_name') or not data.get('parent_email'):
        return jsonify({"error": "Missing required fields (student_name, parent_name, parent_email)"}), 400

    student_name = data.get('student_name')
    student_class = data.get('student_class')
    parent_name = data.get('parent_name')
    parent_email = data.get('parent_email')
    parent_phone = data.get('parent_phone')

    # Fee details (optional)
    fee_amount = data.get('fee_amount')
    fee_due_date = data.get('fee_due_date')
    add_fee_record = fee_amount is not None and fee_due_date is not None and fee_amount != '' and fee_due_date != ''

    connection = None
    cursor = None
    try:
        # Connect to the database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # --- Insert Student --- 
        student_sql = """
            INSERT INTO students (student_name, student_class, parent_name, parent_email, parent_phone)
            VALUES (%s, %s, %s, %s, %s)
        """
        student_values = (student_name, student_class, parent_name, parent_email, parent_phone)
        cursor.execute(student_sql, student_values)
        student_id = cursor.lastrowid
        print(f"Inserted student '{student_name}' with ID: {student_id}")

        # --- Insert Fee Record (if provided) --- 
        fee_message = ""
        if add_fee_record:
            try:
                # Validate fee amount is a number
                fee_amount_float = float(fee_amount)
                # Validate due date format (basic check, assumes YYYY-MM-DD from input type="date")
                datetime.strptime(fee_due_date, '%Y-%m-%d') 

                fee_sql = """
                    INSERT INTO fees (student_name, parent_name, parent_email, amount_due, due_date, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                fee_values = (student_name, parent_name, parent_email, fee_amount_float, fee_due_date, 'Pending')
                cursor.execute(fee_sql, fee_values)
                fee_id = cursor.lastrowid
                print(f"Inserted initial fee record for student '{student_name}' with ID: {fee_id}")
                fee_message = f" Initial fee record added (Amount: {fee_amount_float}, Due: {fee_due_date})."
            except ValueError as ve:
                # Handle invalid fee amount or date format
                connection.rollback() # Rollback student insertion as well if fee fails
                error_message = f"Invalid fee data provided: {ve}"
                print(error_message)
                return jsonify({"error": "Failed to add student due to invalid fee data", "details": error_message}), 400
            except mysql.connector.Error as fee_err:
                 # Handle potential DB errors during fee insertion
                connection.rollback() # Rollback student insertion
                error_message = f"Database error adding fee record: {fee_err}"
                print(error_message)
                return jsonify({"error": "Failed to add fee record", "details": error_message}), 500

        # --- Commit Transaction --- 
        connection.commit()

        # Prepare response data including parent details
        response_data = {
            "message": f"Student '{student_name}' added successfully.{fee_message}",
            "student_id": student_id,
            "parent_details": {
                "name": parent_name,
                "email": parent_email,
                "phone": parent_phone
            }
        }

        return jsonify(response_data), 201

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        error_message = f"Database error: {err}"
        status_code = 500
        if err.errno == 1062: # Duplicate entry for student (e.g., parent email unique constraint)
            error_message = "Error: Parent email already exists in students table."
            status_code = 409 # Conflict
        print(error_message)
        return jsonify({"error": "Failed to add student", "details": error_message}), status_code
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Endpoint to get all students
@app.route('/api/students', methods=['GET'])
def get_students():
    """Endpoint to fetch all student details."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # Changed 'student_id' to 'id'
        cursor.execute("SELECT id, student_name, student_class, parent_name, parent_email, parent_phone FROM students ORDER BY student_name")
        students = cursor.fetchall()

        # Rename 'id' key to 'student_id' for frontend consistency
        for student in students:
            student['student_id'] = student.pop('id')

        return jsonify(students), 200

    except mysql.connector.Error as err:
        print(f"Database error fetching students: {err}")
        return jsonify({"error": "Database error fetching students", "details": str(err)}), 500
    except Exception as e:
        print(f"An unexpected error occurred fetching students: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Endpoint to delete a student
@app.route('/api/delete-student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Endpoint to delete a student by their ID and their associated fee records."""
    connection = None
    cursor = None
    student_name_to_delete = None # Variable to store the student's name

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        # Start transaction
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True) # Use dictionary cursor to get column names

        # --- Step 1: Find the student and get their name ---        
        cursor.execute("SELECT student_name FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        student_name_to_delete = student['student_name'] # Get the student's name

        # --- Step 2: Delete associated fee records using student_name ---        
        if student_name_to_delete:
            print(f"Attempting to delete fee records for student: {student_name_to_delete}")
            fee_delete_sql = "DELETE FROM fees WHERE student_name = %s"
            cursor.execute(fee_delete_sql, (student_name_to_delete,))
            deleted_fees_count = cursor.rowcount
            print(f"Deleted {deleted_fees_count} fee records for student: {student_name_to_delete}")
        else:
             print(f"Warning: Could not retrieve student name for ID {student_id}. Skipping fee deletion.")


        # --- Step 3: Delete the student record ---        
        student_delete_sql = "DELETE FROM students WHERE id = %s"
        cursor.execute(student_delete_sql, (student_id,))
        deleted_student_count = cursor.rowcount

        # --- Step 4: Commit Transaction --- 
        connection.commit()

        if deleted_student_count > 0:
            print(f"Deleted student with ID: {student_id}")
            return jsonify({
                "message": f"Student '{student_name_to_delete}' (ID: {student_id}) and their associated fee records deleted successfully."
            }), 200
        else:
             print(f"Failed to delete student with ID: {student_id} (rowcount 0 after finding them)")             
             return jsonify({"error": "Failed to delete student after finding them."}), 500

    except mysql.connector.Error as err:
        if connection:
            connection.rollback() # Rollback on any DB error
        print(f"Database error deleting student {student_id} or their fees: {err}")
        return jsonify({"error": "Database error during deletion", "details": str(err)}), 500
    except Exception as e:
        if connection:
            connection.rollback() # Rollback on any unexpected error
        print(f"An unexpected error occurred deleting student {student_id}: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# New endpoint to mark a fee as paid (by deleting it)
@app.route('/api/mark-fee-paid/<int:fee_id>', methods=['DELETE'])
def mark_fee_paid(fee_id):
    """Endpoint to mark a fee as paid by deleting the fee record."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        connection.start_transaction() # Use transaction
        cursor = connection.cursor()

        # Check if the fee record exists before deleting
        cursor.execute("SELECT id FROM fees WHERE id = %s", (fee_id,))
        fee = cursor.fetchone()
        if not fee:
            return jsonify({"error": "Fee record not found"}), 404

        # Delete the fee record
        cursor.execute("DELETE FROM fees WHERE id = %s", (fee_id,))
        connection.commit()

        if cursor.rowcount > 0:
            print(f"Deleted fee record with ID: {fee_id} (marked as paid)")
            return jsonify({"message": f"Fee record with ID {fee_id} marked as paid and deleted successfully."}), 200
        else:
            # Should not happen if fetchone() found the record, but good practice
            print(f"Failed to delete fee record with ID: {fee_id} (rowcount 0 after finding it)")
            return jsonify({"error": "Failed to delete fee record after finding it."}), 404 # Or 500

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        print(f"Database error deleting fee record {fee_id}: {err}")
        return jsonify({"error": "Database error marking fee as paid", "details": str(err)}), 500
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"An unexpected error occurred marking fee {fee_id} as paid: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Run the application
if __name__ == "__main__":
    app.run(debug=True)