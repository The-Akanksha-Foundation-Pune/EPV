import os
import sys
from datetime import datetime, timedelta, date

# Set up Flask app context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from models import db, EPV, EPVApproval, SettingsFinance
from smtp_email_utils import send_approval_email


def business_days_between(start_date, end_date):
    """Return the number of business days between two dates (inclusive of start, exclusive of end)."""
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    day_count = 0
    current = start_date
    while current < end_date:
        if current.weekday() < 5:  # 0=Monday, 4=Friday
            day_count += 1
        current += timedelta(days=1)
    return day_count


def send_manager_approval_reminders():
    """Send reminder emails to managers for expenses pending approval beyond max_reminder_days."""
    with app.app_context():
        # Get max_reminder_days from settings, default to 2
        setting = SettingsFinance.query.filter_by(setting_name='max_reminder_days').first()
        try:
            max_reminder_days = int(setting.setting_value) if setting else 2
        except Exception:
            max_reminder_days = 2

        # Find all pending manager approvals for EPVs
        pending_approvals = EPVApproval.query.join(EPV).filter(
            EPVApproval.status == 'pending',
            EPV.status == 'pending_approval'
        ).all()

        # Set the base URL for approval links (change as needed)
        base_url = "http://127.0.0.1:5000"  # Change to your production domain if needed

        today = date.today()
        reminders_sent = 0
        for approval in pending_approvals:
            epv = EPV.query.get(approval.epv_id)
            if epv and epv.status == 'pending_approval' and epv.submission_date:
                business_days = business_days_between(epv.submission_date, today)
                if business_days > max_reminder_days:
                    # Send the approval email with the token
                    send_approval_email(epv, approval.approver_email, base_url, approval.token, is_reminder=True)
                    print(f"Reminder sent to manager for EPV #{epv.id} (Approval ID: {approval.id}, Email: {approval.approver_email}, Token: {approval.token}, Business Days: {business_days})")
                    reminders_sent += 1
        print(f"Total reminders sent: {reminders_sent}")

if __name__ == "__main__":
    send_manager_approval_reminders() 