import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_message(sender, to, subject, html_content):
    """Create a message for an email."""
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)

    # Encode the message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {'raw': encoded_message}

def send_message(credentials, sender, to, subject, html_content):
    """Send an email message."""
    try:
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        # Create the message
        message = create_message(sender, to, subject, html_content)

        # Send the message
        sent_message = service.users().messages().send(userId="me", body=message).execute()

        print(f"Message sent successfully. Message ID: {sent_message['id']}")
        return True, sent_message['id']

    except HttpError as error:
        print(f"An error occurred while sending the email: {error}")
        return False, str(error)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False, str(e)

def create_approval_email(epv_record, sender_email, base_url, token=None):
    """Create an HTML email for expense approval."""
    # Format expense details
    expense_date_range = f"{epv_record.from_date} to {epv_record.to_date}" if epv_record.from_date and epv_record.to_date else "N/A"
    total_amount = f"₹{epv_record.total_amount:.2f}" if epv_record.total_amount else "N/A"

    # Create approval and rejection URLs with token if provided
    if token:
        approve_url = f"{base_url}/approve-expense/{epv_record.epv_id}?token={token}"
        reject_url = f"{base_url}/reject-expense/{epv_record.epv_id}?token={token}"
        view_url = f"{base_url}/epv-record/{epv_record.epv_id}?token={token}"
    else:
        # Fallback to legacy URLs without token
        approve_url = f"{base_url}/approve-expense/{epv_record.epv_id}"
        reject_url = f"{base_url}/reject-expense/{epv_record.epv_id}"
        view_url = f"{base_url}/epv-record/{epv_record.epv_id}"

    # Create HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Expense Approval Request</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #3f51b5;
                color: white;
                padding: 15px;
                border-radius: 5px 5px 0 0;
                text-align: center;
            }}
            .content {{
                padding: 20px;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }}
            .expense-details {{
                margin-bottom: 20px;
            }}
            .expense-details table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .expense-details th, .expense-details td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            .expense-details th {{
                background-color: #f5f5f5;
            }}
            .buttons {{
                margin-top: 30px;
                text-align: center;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin: 0 10px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
                color: white;
            }}
            .approve {{
                background-color: #4CAF50;
            }}
            .reject {{
                background-color: #f44336;
            }}
            .view {{
                background-color: #2196F3;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Expense Approval Request</h2>
        </div>
        <div class="content">
            <p>Dear Approver,</p>
            <p>An expense voucher has been submitted for your approval. Please review the details below:</p>

            <div class="expense-details">
                <table>
                    <tr>
                        <th>EPV ID</th>
                        <td>{epv_record.epv_id}</td>
                    </tr>
                    <tr>
                        <th>Employee</th>
                        <td>{epv_record.employee_name} ({epv_record.employee_id})</td>
                    </tr>
                    <tr>
                        <th>Date Range</th>
                        <td>{expense_date_range}</td>
                    </tr>
                    <tr>
                        <th>Total Amount</th>
                        <td>{total_amount}</td>
                    </tr>
                    <tr>
                        <th>Submitted On</th>
                        <td>{epv_record.submission_date.strftime('%Y-%m-%d') if epv_record.submission_date else 'N/A'}</td>
                    </tr>
                </table>
            </div>

            <div class="buttons">
                <a href="{view_url}" class="button view">View Details</a>
                <a href="{approve_url}" class="button approve">Approve</a>
                <a href="{reject_url}" class="button reject">Reject</a>
            </div>

            <p>If you have any questions, please contact the submitter at {epv_record.email_id}.</p>

            <div class="footer">
                <p>This is an automated email from the Expense Management System. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content

def send_approval_email(epv_record, approver_email, credentials, base_url, token=None):
    """Send an approval email for an expense record."""
    # Get sender email from credentials or use a default
    sender_email = "expense.system@akanksha.org"

    # Create email subject
    subject = f"Expense Approval Request: {epv_record.epv_id}"

    # Create HTML content with token for secure approval/rejection
    html_content = create_approval_email(epv_record, sender_email, base_url, token)

    # Send the email
    return send_message(credentials, sender_email, approver_email, subject, html_content)
