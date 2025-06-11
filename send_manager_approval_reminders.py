import os
import sys
from datetime import datetime, timedelta

# Set up Flask app context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from models import db, EPV, EPVApproval, SettingsFinance
from smtp_email_utils import send_approval_email


def send_manager_approval_reminders():
    """Send reminder emails to managers for expenses pending approval beyond max_reminder_days."""
    with app.app_context():
        # Get max_reminder_days from settings, default to 2
        setting = SettingsFinance.query.filter_by(setting_name='max_reminder_days').first()
        try:
            max_reminder_days = int(setting.setting_value) if setting else 2
        except Exception:
            max_reminder_days = 2
        threshold_date = datetime.now() - timedelta(days=max_reminder_days)

        # Find all pending manager approvals for EPVs older than threshold
        pending_approvals = EPVApproval.query.join(EPV).filter(
            EPVApproval.status == 'pending',
            EPV.status == 'pending_approval',
            EPV.submission_date <= threshold_date
        ).all()

        # Set the base URL for approval links (change as needed)
        base_url = "http://127.0.0.1:5000"  # Change to your production domain if needed

        print(f"Found {len(pending_approvals)} pending manager approvals older than {max_reminder_days} days.")
        for approval in pending_approvals:
            epv = EPV.query.get(approval.epv_id)
            if epv and epv.status == 'pending_approval':
                # Send the approval email with the token
                send_approval_email(epv, approval.approver_email, base_url, approval.token, is_reminder=True)
                print(f"Reminder sent to manager for EPV #{epv.id} (Approval ID: {approval.id}, Email: {approval.approver_email}, Token: {approval.token})")

if __name__ == "__main__":
    send_manager_approval_reminders() 