from datetime import datetime, timedelta
from models.fee_record import FeeRecord

def detect_pending_fees(fee_records):
    pending_fees = []
    today = datetime.now().date()
    for record in fee_records:
        if record.status == "Pending":
            days_left = (record.due_date - today).days
            if days_left > 7:
                urgency = "Due in 7+ days"
            elif 3 <= days_left <= 6:
                urgency = "Due in 3–6 days"
            else:
                urgency = "Overdue"
            pending_fees.append((record, urgency))
    return pending_fees