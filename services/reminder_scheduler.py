from datetime import datetime, timedelta

def schedule_reminders(fee_record, payment_behavior):
    reminders = []
    today = datetime.now().date()
    first_reminder = fee_record.due_date - timedelta(days=7)
    second_reminder = fee_record.due_date - timedelta(days=3)
    last_reminder = fee_record.due_date
    follow_up_reminder = fee_record.due_date + timedelta(days=1)

    if payment_behavior == "late":
        first_reminder = fee_record.due_date - timedelta(days=10)

    if today <= first_reminder:
        reminders.append((first_reminder, "First Reminder"))
    if today <= second_reminder:
        reminders.append((second_reminder, "Second Reminder"))
    if today <= last_reminder:
        reminders.append((last_reminder, "Last Reminder"))
    if today > last_reminder:
        reminders.append((follow_up_reminder, "Follow-up Reminder"))

    return reminders