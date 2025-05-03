class FeeRecord:
    def __init__(self, student_name, parent_name, amount_due, due_date, parent_email):
        self.student_name = student_name
        self.parent_name = parent_name
        self.amount_due = amount_due
        self.due_date = due_date
        self.parent_email = parent_email
        self.status = "Pending"  # Default status is pending