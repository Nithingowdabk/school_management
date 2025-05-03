# TeacherPerformanceAI.py


import mysql.connector

# Weightage constants
WEIGHT_FEEDBACK = 0.3
WEIGHT_ATTENDANCE = 0.25
WEIGHT_RESULT = 0.3
WEIGHT_ACTIVITIES = 0.15

RATING_THRESHOLDS = {
    "Excellent": 85,
    "Very Good": 75,
    "Good": 60,
    "Needs Improvement": 0
}

SUGGESTIONS = {
    "Excellent": "Keep it up!",
    "Very Good": "Maintain consistency!",
    "Good": "Focus on results.",
    "Needs Improvement": "Improve in all areas."
}

def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your actual username
        password="Nithin2003",  # Replace with your actual password
        database="school_management"  # Replace with your actual database name
    )

def setup_feedback_table():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Create the feedback table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            teacher_name VARCHAR(255) NOT NULL,
            feedback_score FLOAT NOT NULL
        )
    """)

    # Insert sample data into the feedback table
    cursor.execute("""
        INSERT INTO feedback (teacher_name, feedback_score) VALUES
        ('John Doe', 4.5),
        ('Jane Smith', 4.0)
    """)

    connection.commit()
    cursor.close()
    connection.close()

def setup_attendance_table():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Create the attendance table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            teacher_name VARCHAR(255) NOT NULL,
            attendance_percentage FLOAT NOT NULL
        )
    """)

    # Insert sample data into the attendance table
    cursor.execute("""
        INSERT INTO attendance (teacher_name, attendance_percentage) VALUES
        ('John Doe', 95.0),
        ('Jane Smith', 88.0)
    """)

    connection.commit()
    cursor.close()
    connection.close()

def setup_results_table():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Create the results table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            teacher_name VARCHAR(255) NOT NULL,
            result_percentage FLOAT NOT NULL
        )
    """)

    # Insert sample data into the results table
    cursor.execute("""
        INSERT INTO results (teacher_name, result_percentage) VALUES
        ('John Doe', 90.0),
        ('Jane Smith', 85.0)
    """)

    connection.commit()
    cursor.close()
    connection.close()

def setup_extra_activities_table():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Create the extra_activities table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extra_activities (
            teacher_name VARCHAR(255) NOT NULL,
            activity_score FLOAT NOT NULL
        )
    """)

    # Insert sample data into the extra_activities table
    cursor.execute("""
        INSERT INTO extra_activities (teacher_name, activity_score) VALUES
        ('John Doe', 4.8),
        ('Jane Smith', 4.2)
    """)

    connection.commit()
    cursor.close()
    connection.close()

def get_feedback_scores():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT teacher_name, feedback_score FROM feedback")
    feedback_scores = {row['teacher_name']: row['feedback_score'] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return feedback_scores

def get_attendance_data():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT teacher_name, attendance_percentage FROM attendance")
    attendance_data = {row['teacher_name']: row['attendance_percentage'] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return attendance_data

def get_result_data():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT teacher_name, result_percentage FROM results")
    result_data = {row['teacher_name']: row['result_percentage'] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return result_data

def get_extra_activity_scores():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT teacher_name, activity_score FROM extra_activities")
    activity_scores = {row['teacher_name']: row['activity_score'] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return activity_scores

def calculate_final_score(feedback, attendance, result, activity):
    return (feedback * 20 * WEIGHT_FEEDBACK +
            attendance * WEIGHT_ATTENDANCE +
            result * WEIGHT_RESULT +
            activity * 100 * WEIGHT_ACTIVITIES)

def get_rating_and_suggestion(score):
    for rating, threshold in RATING_THRESHOLDS.items():
        if score >= threshold:
            return rating, SUGGESTIONS[rating]
    return "", ""

def setup_teacher_performance_table():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Clear existing data from the teacher_performance table first
    cursor.execute("DELETE FROM teacher_performance")
    connection.commit() # Commit the deletion

    # Create the teacher_performance table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_performance (
            teacher_name VARCHAR(255) NOT NULL,
            feedback_score FLOAT NOT NULL,
            attendance_percentage FLOAT NOT NULL,
            result_percentage FLOAT NOT NULL,
            activity_score FLOAT NOT NULL,
            final_score FLOAT NOT NULL,
            rating VARCHAR(50) NOT NULL,
            ai_suggestion TEXT NOT NULL
        )
    """)

    # Fetch data from individual tables
    feedback_scores = get_feedback_scores()
    attendance_data = get_attendance_data()
    result_data = get_result_data()
    activity_scores = get_extra_activity_scores()

    # Populate the teacher_performance table
    for teacher in feedback_scores.keys():
        feedback = feedback_scores.get(teacher, 0)
        attendance = attendance_data.get(teacher, 0)
        result = result_data.get(teacher, 0)
        activity = activity_scores.get(teacher, 0)

        final_score = calculate_final_score(feedback, attendance, result, activity)
        rating, suggestion = get_rating_and_suggestion(final_score)

        cursor.execute("""
            INSERT INTO teacher_performance (
                teacher_name, feedback_score, attendance_percentage, result_percentage, activity_score, final_score, rating, ai_suggestion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (teacher, feedback, attendance, result, activity, final_score, rating, suggestion))

    connection.commit()
    cursor.close()
    connection.close()

def main():
    # Ensure all necessary tables exist and have data before populating teacher_performance
    setup_feedback_table()
    setup_attendance_table()
    setup_results_table()
    setup_extra_activities_table()

    # Now, setup/populate the main performance table
    setup_teacher_performance_table() # This function now handles fetching and inserting

    # Fetch the final data for printing (optional, as it's already in the table)
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teacher_performance")
    performance_data = cursor.fetchall()
    cursor.close()
    connection.close()

    print("\nTeacher Performance Data (from teacher_performance table):")
    print(f"{'Teacher Name':<15} {'Feedback':<10} {'Attendance':<12} {'Result':<8} {'Activity':<10} {'Final Score':<12} {'Rating':<15} {'AI Suggestion'}")
    print("-" * 110) # Adjusted separator length

    for teacher in performance_data:
        print(f"{teacher['teacher_name']:<15} {teacher['feedback_score']}/5     {teacher['attendance_percentage']}%       {teacher['result_percentage']}%     {teacher['activity_score']}/5      {round(teacher['final_score'])}%         {teacher['rating']:<15} {teacher['ai_suggestion']}")


if __name__ == "__main__":
    main() # Run the main logic to populate the table
