import os
import uuid
import re
import pymysql
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, session, jsonify, request, send_file
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from models import db, CostCenter, EmployeeDetails, SettingsFinance, ExpenseHead, EPV, EPVItem, init_db
from pdf_converter import process_files
from google.oauth2.credentials import Credentials

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Motoming%40123@127.0.0.1:3306/AFDW"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Configure OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/gmail.send'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

# Routes
@app.route('/')
def index():
    # Check if user is logged in
    user_info = session.get('user_info')
    if user_info:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login')
def login():
    # Store the original URL the user was trying to access
    next_url = request.args.get('next') or request.referrer or '/dashboard'
    session['next_url'] = next_url
    print(f"DEBUG: Storing next_url in session: {next_url}")

    # Use the exact redirect URI configured in Google API Console
    redirect_uri = 'http://127.0.0.1:5000/login/google/authorized'
    print(f"DEBUG: Redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def authorize():
    try:
        # Get the authorization response
        token = google.authorize_access_token()
        print(f"DEBUG: Token received: {token}")

        # Get user info from Google
        resp = google.get('userinfo')
        user_info = resp.json()
        print(f"DEBUG: User info: {user_info}")

        # Store user info and token in session
        session['user_info'] = user_info
        session['google_token'] = token
        session['email'] = user_info['email']  # Store email in session
        print(f"DEBUG: Stored Google token in session: {token}")

        # Print token details for debugging
        if 'access_token' in token:
            print(f"DEBUG: Access token: {token['access_token'][:10]}...")
        if 'refresh_token' in token:
            print(f"DEBUG: Refresh token available: Yes")
        else:
            print(f"DEBUG: Refresh token available: No")

        # Check if the user exists in the employee_details table
        print(f"DEBUG: Checking if user {user_info['email']} exists in employee_details table...")
        # Print all employees in the table
        all_employees = EmployeeDetails.query.all()
        print(f"DEBUG: Found {len(all_employees)} employees in the database.")

        # Execute a direct SQL query to check the database
        from sqlalchemy import text
        result = db.session.execute(text("SELECT * FROM employee_details"))
        rows = result.fetchall()
        print(f"DEBUG: Direct SQL query found {len(rows)} employees.")

        # Print the first 5 employees from the query
        for i, row in enumerate(rows[:5]):
            print(f"DEBUG: SQL row {i}: {row}")

        # Print all employees from the ORM query
        for emp in all_employees:
            print(f"DEBUG: Employee in DB: {emp.email}, {emp.name}, {emp.role}")

        # Case-insensitive comparison for email
        user_email = user_info['email'].lower()
        print(f"DEBUG: Looking for email (lowercase): {user_email}")

        # Try direct SQL query for the email
        sql_result = db.session.execute(text(f"SELECT * FROM employee_details WHERE email = '{user_email}'"))
        sql_row = sql_result.fetchone()
        if sql_row:
            print(f"DEBUG: SQL query found employee with exact email: {sql_row}")
        else:
            print(f"DEBUG: SQL query did not find employee with email: {user_email}")
            # Try case-insensitive SQL query
            sql_result = db.session.execute(text(f"SELECT * FROM employee_details WHERE LOWER(email) = '{user_email}'"))
            sql_row = sql_result.fetchone()
            if sql_row:
                print(f"DEBUG: SQL query found employee with case-insensitive email: {sql_row}")
            else:
                print(f"DEBUG: SQL query did not find employee with case-insensitive email: {user_email}")

        # Try direct comparison first
        employee = EmployeeDetails.query.filter_by(email=user_email).first()
        if employee:
            print(f"DEBUG: Found employee using exact match: {employee.email}")
        else:
            print("DEBUG: No exact match found, trying case-insensitive search...")
            # Try case-insensitive search
            employee = EmployeeDetails.query.filter(EmployeeDetails.email.ilike(f"%{user_email}%")).first()
            if employee:
                print(f"DEBUG: Found employee using case-insensitive match: {employee.email}")
            else:
                print("DEBUG: No employee found with either method.")
        if employee:
            # Store employee details in session
            session['employee_role'] = employee.role
            session['employee_manager'] = employee.manager
            session['employee_id'] = employee.employee_id
            print(f"DEBUG: Employee found in database. Role: {employee.role}, Manager: {employee.manager}")
        else:
            # User not found in employee_details
            session['employee_role'] = None
            session['employee_manager'] = None
            session['employee_id'] = None
            print(f"DEBUG: Employee not found in database: {user_info['email']}")

        # Redirect to the original URL the user was trying to access
        next_url = session.pop('next_url', '/dashboard')
        print(f"DEBUG: Redirecting to: {next_url}")

        # Use a minimal redirect page that maintains the auth flow flag
        response_html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Redirecting...</title>
            <script>
                // This script will be executed when the page loads
                document.addEventListener('DOMContentLoaded', function() {
                    // Record the time when this page loaded
                    const startTime = new Date().getTime();

                    // Store the start time in localStorage
                    localStorage.setItem('loginStartTime', startTime);

                    // Maintain the auth flow flag
                    if (!sessionStorage.getItem('authFlowInProgress')) {
                        sessionStorage.setItem('authFlowInProgress', 'true');
                    }

                    // Redirect immediately to the target page
                    window.location.href = "REDIRECT_URL";
                });
            </script>
        </head>
        <body style="margin: 0; padding: 0; height: 100vh; overflow: hidden; background-color: #f5f5f5;">
            <!-- Intentionally empty - we're maintaining the loading screen from the previous page -->
        </body>
        </html>
        '''

        # Set the redirect URL based on the next_url
        if next_url == '/epv-records' or next_url.endswith('/epv-records'):
            redirect_url = '/epv-records'
        else:
            # Default to dashboard
            redirect_url = url_for('dashboard')

        # Replace the placeholder with the actual redirect URL
        response_html = response_html.replace('REDIRECT_URL', redirect_url)

        # Return the HTML with the timing script
        return response_html
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    print(f"DEBUG: Dashboard accessed by {user_info.get('email')}")
    print(f"DEBUG: Employee role: {employee_role}, Manager: {employee_manager}, ID: {employee_id}")

    return render_template('dashboard_new.html')

@app.route('/logout')
def logout():
    # Clear entire session
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/user')
def get_user():
    user_info = session.get('user_info')
    if not user_info:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify(user_info)

# Add a route to view cost centers
@app.route('/cost-centers')
def cost_centers():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    # Get all cost centers
    cost_centers = CostCenter.query.all()
    return render_template('cost_centers.html',
                           cost_centers=cost_centers,
                           user=user_info,
                           employee_role=employee_role,
                           employee_manager=employee_manager,
                           employee_id=employee_id)

# Add a route to add/edit approver email
@app.route('/cost-centers/<int:id>/edit', methods=['GET', 'POST'])
def edit_cost_center(id):
    from flask import request

    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get the cost center
    cost_center = CostCenter.query.get_or_404(id)

    if request.method == 'POST':
        # Update the cost center
        cost_center.approver_email = request.form.get('approver_email')
        cost_center.drive_id = request.form.get('drive_id')
        db.session.commit()
        return redirect(url_for('cost_centers'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    return render_template('edit_cost_center.html',
                           cost_center=cost_center,
                           user=user_info,
                           employee_role=employee_role,
                           employee_manager=employee_manager,
                           employee_id=employee_id)

# Add a route to view employee details
@app.route('/employees')
def employees():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    # Get all employees
    employees = EmployeeDetails.query.all()
    return render_template('employees.html',
                           employees=employees,
                           user=user_info,
                           employee_role=employee_role,
                           employee_manager=employee_manager,
                           employee_id=employee_id)

# Add a route to edit employee details
@app.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
def edit_employee(id):
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get the employee
    employee = EmployeeDetails.query.get_or_404(id)

    if request.method == 'POST':
        # Update the employee
        employee.name = request.form.get('name')
        employee.employee_id = request.form.get('employee_id')
        employee.manager = request.form.get('manager')
        employee.role = request.form.get('role')
        db.session.commit()
        return redirect(url_for('employees'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    return render_template('edit_employee.html',
                           employee=employee,
                           user=user_info,
                           employee_role=employee_role,
                           employee_manager=employee_manager,
                           employee_id=employee_id)

# Add a route for the new expense form
@app.route('/new-expense', methods=['GET', 'POST'])
def new_expense():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get employee details from session
    employee_role = session.get('employee_role')
    employee_manager = session.get('employee_manager')
    employee_id = session.get('employee_id')

    # Get all cost centers for the dropdown
    cost_centers = CostCenter.query.all()

    # Get all employees for the autocomplete
    employees = EmployeeDetails.query.all()

    # Get all active expense heads
    expense_heads = ExpenseHead.query.filter_by(is_active=True).all()

    # Handle form submission
    if request.method == 'POST':
        try:
            # Process the expense form data

            # Get form data
            employee_name = request.form.get('employee_name')  # Changed from 'employeeName' to match the form field name
            cost_center_id = request.form.get('cost_center')  # Changed from 'costCenter' to match the form field name

            # Get cost center details for Google Drive upload
            cost_center = None
            drive_folder_id = None
            cost_center_name = None

            print(f"DEBUG: Selected cost_center_id: {cost_center_id}")

            # List all cost centers and their drive IDs for debugging
            try:
                all_cost_centers = CostCenter.query.all()
                print(f"DEBUG: All cost centers in database:")
                for cc in all_cost_centers:
                    print(f"DEBUG: ID: {cc.id}, Name: {cc.costcenter}, Drive ID: {cc.drive_id}")
            except Exception as e:
                print(f"ERROR: Failed to list all cost centers: {str(e)}")

            if cost_center_id:
                try:
                    # First try with string comparison
                    cost_center = CostCenter.query.filter_by(id=cost_center_id).first()
                    print(f"DEBUG: Cost center lookup result: {cost_center}")

                    if cost_center:
                        cost_center_name = cost_center.costcenter
                        drive_folder_id = cost_center.drive_id
                        print(f"DEBUG: Found cost center: {cost_center_name}, Drive folder ID: {drive_folder_id}")

                        # Check if drive_folder_id is None or empty
                        if not drive_folder_id or drive_folder_id.strip() == "":
                            print(f"WARNING: Drive folder ID is empty or None for cost center {cost_center_name}")
                    else:
                        print(f"WARNING: No cost center found with ID: {cost_center_id}")

                        # Try with integer ID if string lookup failed
                        try:
                            int_id = int(cost_center_id)
                            cost_center = CostCenter.query.filter_by(id=int_id).first()
                            if cost_center:
                                cost_center_name = cost_center.costcenter
                                drive_folder_id = cost_center.drive_id
                                print(f"DEBUG: Found cost center with int ID: {cost_center_name}, Drive folder ID: {drive_folder_id}")
                        except ValueError:
                            print(f"DEBUG: cost_center_id is not an integer: {cost_center_id}")
                except Exception as e:
                    print(f"ERROR: Failed to get cost center details: {str(e)}")

            # Debug request.files
            print(f"DEBUG: request.files keys: {list(request.files.keys())}")
            for key in request.files.keys():
                file = request.files[key]
                print(f"DEBUG: File key: {key}, filename: {file.filename if file else 'None'}")

            # Generate a unique EPV ID for this expense
            # Format: EPV-YYYYMMDD-XXXXXXXXXX (10 hex chars from UUID for near-absolute uniqueness)
            epv_id = f"EPV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:10].upper()}"

            # Prepare expense data structure
            expense_data = {
                'employee_id': employee_id,
                'employee_name': employee_name,
                'from_date': request.form.get('from_date'),
                'to_date': request.form.get('to_date'),
                'cost_center': cost_center_name,
                'expense_type': request.form.get('expense_type'),
                'epv_id': epv_id,
                'expenses': []
            }

            # Extract expense items from form data
            i = 0
            while f'expenses[{i}][invoice_date]' in request.form:
                expense = {
                    'invoice_date': request.form.get(f'expenses[{i}][invoice_date]'),
                    'expense_head': request.form.get(f'expenses[{i}][expense_head]'),
                    'amount': request.form.get(f'expenses[{i}][amount]'),
                    'description': request.form.get(f'expenses[{i}][description]'),
                    'split_invoice': request.form.get(f'expenses[{i}][split_invoice]') == '1'
                }
                expense_data['expenses'].append(expense)
                i += 1

            # Calculate total amount
            total_amount = sum(float(expense['amount']) for expense in expense_data['expenses'] if expense['amount'])
            expense_data['total_amount'] = f"{total_amount:.2f}"

            # Identify split invoices
            split_invoice_indices = []
            for i, expense in enumerate(expense_data['expenses']):
                if expense.get('split_invoice'):
                    split_invoice_indices.append(i)
                    print(f"DEBUG: Expense #{i+1} is marked as a split invoice, will skip receipt upload")

            # Process files based on split invoice information
            expense_files = []
            for key, file in request.files.items():
                if ('receipt' in key or 'receipt_upload' in key) and file.filename:
                    # Extract the index from the key (e.g., expenses[0][receipt] -> 0)
                    try:
                        index_match = re.search(r'expenses\[(\d+)\]', key)
                        if index_match:
                            index = int(index_match.group(1))
                            # Skip if this is a split invoice
                            if index in split_invoice_indices:
                                print(f"DEBUG: Skipping file for split invoice: {key} = {file.filename}")
                                continue
                    except Exception as e:
                        print(f"DEBUG: Error parsing index from key {key}: {str(e)}")

                    print(f"DEBUG: Adding file to process: {key} = {file.filename}")
                    expense_files.append(file)

            # Generate expense document PDF
            from pdf_converter import generate_expense_document
            expense_pdf_path = generate_expense_document(expense_data)

            if not expense_pdf_path:
                return jsonify({
                    'success': False,
                    'message': 'Failed to generate expense document'
                })

            # Debug print expense type
            print(f"DEBUG: expense_type from form: {request.form.get('expense_type')}")

            # Save expense data to the database
            try:
                # Create new EPV record
                new_epv = EPV(
                    epv_id=epv_id,
                    email_id=session.get('email', ''),  # Capture the user's email
                    employee_name=employee_name,
                    employee_id=employee_id,
                    from_date=datetime.strptime(request.form.get('from_date'), '%Y-%m-%d'),
                    to_date=datetime.strptime(request.form.get('to_date'), '%Y-%m-%d'),
                    payment_to=request.form.get('expense_type', 'General Expense'),  # Default value if not provided
                    submission_date=datetime.now(),
                    academic_year=f"{datetime.now().year}-{datetime.now().year + 1}",
                    cost_center_id=cost_center_id,
                    cost_center_name=cost_center_name,
                    total_amount=float(expense_data['total_amount']),
                    amount_in_words=expense_data.get('amount_in_words', ''),
                    status='submitted'
                )

                db.session.add(new_epv)
                db.session.flush()  # Get the ID without committing

                # Add expense items
                for expense in expense_data['expenses']:
                    item = EPVItem(
                        epv_id=new_epv.id,
                        expense_invoice_date=datetime.strptime(expense['invoice_date'], '%Y-%m-%d'),
                        expense_head=expense['expense_head'],
                        description=expense['description'],
                        amount=float(expense['amount']),
                        gst=0.0,  # Default value, can be updated later
                        split_invoice=expense.get('split_invoice', False)  # Include the split invoice flag
                    )
                    db.session.add(item)

                db.session.commit()
                print(f"DEBUG: Saved expense data to database with EPV ID: {epv_id}")
                print(f"DEBUG: EPV record ID: {new_epv.id}")

            except Exception as e:
                db.session.rollback()
                print(f"ERROR saving expense data to database: {str(e)}")
                import traceback
                print(f"DEBUG: Exception traceback: {traceback.format_exc()}")
                # Continue with file processing even if database save fails

            # Process the files if any were uploaded
            if expense_files:
                try:

                    # We already checked expense_pdf_path above

                    # Process the files: save, convert to PDF, merge with expense document, and upload to Google Drive
                    result = process_files(
                        files=expense_files,
                        drive_folder_id=drive_folder_id,
                        employee_name=employee_name,
                        cost_center_name=cost_center_name,
                        expense_pdf_path=expense_pdf_path
                    )

                    # Prepare the response data
                    response_data = {
                        'success': True,
                        'message': 'Expense submitted successfully!',
                        'epv_id': epv_id  # Include the EPV ID in the response
                    }

                    # Handle successful PDF creation
                    if result['success'] and result.get('merged_pdf'):
                        # Store the merged PDF path in session for download
                        merged_pdf_path = result['merged_pdf']
                        session['merged_pdf_path'] = merged_pdf_path

                        # Add download link to response
                        response_data['pdf_url'] = '/download-pdf'

                        # Add Google Drive information
                        # First, indicate whether Drive upload was attempted
                        response_data['drive_attempted'] = result.get('drive_upload_attempted', False)

                        # If upload was successful, add file ID and URL
                        if result.get('drive_file_id'):
                            file_id = result['drive_file_id']
                            response_data['drive_file_id'] = file_id
                            response_data['drive_message'] = f"File uploaded to Google Drive for {cost_center_name if cost_center_name else 'your cost center'}"

                            # Add Drive file URL if available
                            if result.get('drive_file_url'):
                                file_url = result['drive_file_url']
                                response_data['drive_file_url'] = file_url

                                # Update the EPV record with the file URL and Drive ID
                                try:
                                    if 'new_epv' in locals() and new_epv:
                                        new_epv.file_url = file_url
                                        new_epv.drive_file_id = file_id
                                        db.session.commit()
                                        print(f"Updated EPV record with file URL: {file_url}")
                                except Exception as e:
                                    db.session.rollback()
                                    print(f"Error updating EPV record with file URL: {str(e)}")

                        # Add Drive error if any
                        if result.get('drive_error'):
                            response_data['drive_error'] = result['drive_error']
                        # If no drive folder ID was provided, add a specific message
                        elif drive_folder_id is None and cost_center_id:
                            response_data['drive_error'] = f"No Google Drive folder ID found for the selected cost center: {cost_center_name if cost_center_name else cost_center_id}"

                        # Add warnings if any
                        if result.get('warnings'):
                            response_data['warnings'] = result['warnings']
                            response_data['warning_message'] = result.get('user_message', 'Some files had issues during processing.')

                    # Handle processing errors
                    elif not result['success']:
                        # Processing failed but we still want to submit the form
                        error_msg = result.get('error') or "Failed to process files."
                        user_msg = result.get('user_message') or "There was an issue with the file processing."

                        response_data['error'] = error_msg
                        response_data['error_message'] = user_msg

                        # Add detailed processing results if available
                        if result.get('processing_results'):
                            file_errors = []
                            for file_result in result['processing_results']:
                                if not file_result['success'] and file_result.get('error'):
                                    file_errors.append({
                                        'filename': file_result['filename'],
                                        'error': file_result['error']
                                    })
                            if file_errors:
                                response_data['file_errors'] = file_errors

                    return jsonify(response_data)
                except Exception as e:
                    print(f"Error processing files: {str(e)}")
                    return jsonify({
                        'success': True,
                        'message': 'Expense submitted successfully, but there was an error processing the files.',
                        'error': str(e)
                    })

            # If we get here, either no files were uploaded or processing failed
            # If no files were uploaded, serve the expense document PDF
            if not expense_files:
                try:
                    # Generate a filename for download
                    download_filename = f"Expense_{employee_name}_{cost_center_name}_{datetime.now().strftime('%Y-%m-%d')}.pdf"

                    # If drive_folder_id is provided, upload to Google Drive
                    if drive_folder_id:
                        from drive_utils import upload_file_to_drive, get_file_url
                        drive_file_id = upload_file_to_drive(expense_pdf_path, download_filename, drive_folder_id)

                        if drive_file_id and drive_file_id != 'local_file':
                            drive_file_url = get_file_url(drive_file_id)
                            return jsonify({
                                'success': True,
                                'message': 'Expense document uploaded to Google Drive',
                                'drive_file_url': drive_file_url
                            })

                    # Store the PDF path in session for download
                    session['merged_pdf_path'] = expense_pdf_path

                    return jsonify({
                        'success': True,
                        'message': 'Expense submitted successfully!',
                        'pdf_url': '/download-pdf'
                    })
                except Exception as e:
                    print(f"Error serving expense PDF: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': f"Error serving expense PDF: {str(e)}"
                    })

            # Otherwise, just return success
            return jsonify({
                'success': True,
                'message': 'Expense submitted successfully!',
                'epv_id': epv_id,
                'manager_email': session.get('employee_manager', '')
            })
        except Exception as e:
            print(f"Unexpected error in expense submission: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error submitting expense.',
                'error': str(e)
            }), 500

    # For GET requests, render the form
    return render_template('new_expense.html',
                           user=user_info,
                           employee_role=employee_role,
                           employee_manager=employee_manager,
                           employee_id=employee_id,
                           cost_centers=cost_centers,
                           employees=employees,
                           expense_heads=expense_heads)

# Add an API endpoint to get employee details
@app.route('/api/employees')
def get_employees():
    # Get all employees
    employees = EmployeeDetails.query.all()

    # Convert to JSON
    employee_list = [{
        'id': emp.id,
        'name': emp.name,
        'email': emp.email,
        'employee_id': emp.employee_id
    } for emp in employees if emp.name]

    return jsonify(employee_list)

# Add an API endpoint to get finance settings
@app.route('/api/settings/finance')
def get_finance_settings():
    # Get all finance settings
    settings = SettingsFinance.query.all()

    # Convert to JSON
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.setting_name] = {
            'value': setting.setting_value,
            'description': setting.description,
            'parent_drive_folder': setting.parent_drive_folder,
            'parent_drive_id': setting.parent_drive_id
        }

    return jsonify(settings_dict)

# Add a route to download the merged PDF
@app.route('/download-pdf')
def download_pdf():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get the PDF path from session
    pdf_path = session.get('merged_pdf_path')
    if not pdf_path:
        return jsonify({'error': 'No PDF file available'}), 404

    # Check if the file exists
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404

    # Return the file for download
    try:
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='expense_receipts.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error downloading PDF: {str(e)}")
        return jsonify({'error': f'Error downloading PDF: {str(e)}'}), 500

# Add an API endpoint to get expense heads
@app.route('/api/expense-heads')
def get_expense_heads():
    # Get all active expense heads
    expense_heads = ExpenseHead.query.filter_by(is_active=True).all()

    # Convert to JSON
    expense_head_list = [{
        'id': head.id,
        'head_name': head.head_name,
        'head_code': head.head_code,
        'description': head.description
    } for head in expense_heads]

    return jsonify(expense_head_list)

# Add a route to reset the database (for development only)
@app.route('/reset-db')
def reset_db():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Drop all tables and recreate them
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_db(app)

    return redirect(url_for('dashboard'))

# Add a route to view settings (for development only)
@app.route('/view-settings')
def view_settings():
    # Check if user is logged in
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('index'))

    # Get all settings
    settings = SettingsFinance.query.all()

    # Create a simple HTML table to display settings
    html = '<html><head><title>Settings</title><style>table {border-collapse: collapse; width: 100%;} th, td {border: 1px solid #ddd; padding: 8px; text-align: left;} tr:nth-child(even) {background-color: #f2f2f2;} th {background-color: #4CAF50; color: white;}</style></head><body>'
    html += '<h1>Finance Settings</h1>'
    html += '<table>'
    html += '<tr><th>ID</th><th>Setting Name</th><th>Setting Value</th><th>Description</th><th>Parent Drive Folder</th><th>Parent Drive ID</th></tr>'

    for setting in settings:
        html += f'<tr>'
        html += f'<td>{setting.id}</td>'
        html += f'<td>{setting.setting_name}</td>'
        html += f'<td>{setting.setting_value}</td>'
        html += f'<td>{setting.description}</td>'
        html += f'<td>{setting.parent_drive_folder}</td>'
        html += f'<td>{setting.parent_drive_id}</td>'
        html += f'</tr>'

    html += '</table>'

    # Get all cost centers
    cost_centers = CostCenter.query.all()

    html += '<h1>Cost Centers with Drive IDs</h1>'
    html += '<table>'
    html += '<tr><th>ID</th><th>Cost Center</th><th>City</th><th>Drive ID</th></tr>'

    for cc in cost_centers:
        html += f'<tr>'
        html += f'<td>{cc.id}</td>'
        html += f'<td>{cc.costcenter}</td>'
        html += f'<td>{cc.city}</td>'
        html += f'<td>{cc.drive_id or "Not set"}</td>'
        html += f'</tr>'

    html += '</table>'
    html += '<p><a href="/dashboard">Back to Dashboard</a></p>'
    html += '</body></html>'

    return html

# Route to handle approval requests
@app.route('/send-for-approval', methods=['POST'])
def send_for_approval():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'You must be logged in to send approval requests'}), 401

    try:
        data = request.json
        epv_id = data.get('epv_id')
        approval_option = data.get('approval_option')
        emails = []

        if approval_option == 'yes':
            manager_email = data.get('manager_email')
            if manager_email:
                emails = [manager_email]
        else:
            emails = data.get('custom_emails', [])

        if not epv_id:
            return jsonify({'success': False, 'message': 'EPV ID is required'}), 400

        if not emails:
            return jsonify({'success': False, 'message': 'At least one email address is required'}), 400

        # Find the EPV record
        epv = EPV.query.filter_by(epv_id=epv_id).first()
        if not epv:
            return jsonify({'success': False, 'message': 'EPV record not found'}), 404

        # Get Google credentials from session
        if 'google_token' not in session:
            return jsonify({'success': False, 'message': 'Google authentication required'}), 401

        # Create credentials object
        token_info = session['google_token']
        credentials = Credentials(
            token=token_info['access_token'],
            refresh_token=token_info.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )

        # Import email utilities
        from email_utils import send_approval_email

        # Get base URL for approval links
        if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
            base_url = f"http://{request.host}"
        else:
            base_url = f"https://{request.host}"

        # Import uuid for generating tokens
        import uuid
        from models import EPVApproval

        # Send emails to all approvers
        success_count = 0
        for approver_email in emails:
            try:
                # Create a unique token for this approval
                token = str(uuid.uuid4())

                # Create an EPVApproval record
                approval = EPVApproval(
                    epv_id=epv.id,
                    approver_email=approver_email,
                    status='pending',
                    token=token
                )
                db.session.add(approval)

                # Send the approval email with the token
                success, message_id = send_approval_email(epv, approver_email, credentials, base_url, token)
                if success:
                    success_count += 1
                    # Store approver email in EPV record (legacy support)
                    if not epv.approver_emails:
                        epv.approver_emails = approver_email
                    else:
                        epv.approver_emails += f", {approver_email}"
            except Exception as email_error:
                print(f"Error sending email to {approver_email}: {str(email_error)}")

        # Update the EPV record to indicate approval has been requested
        epv.status = 'pending_approval'
        db.session.commit()

        if success_count > 0:
            return jsonify({
                'success': True,
                'message': f"Approval request sent to {success_count} recipient(s)"
            })
        else:
            return jsonify({
                'success': False,
                'message': "Failed to send approval emails. Please try again later."
            }), 500

    except Exception as e:
        print(f"Error sending approval request: {str(e)}")
        return jsonify({'success': False, 'message': f"Error: {str(e)}"}), 500

# Route to approve an expense
@app.route('/approve-expense/<epv_id>')
def approve_expense(epv_id):
    try:
        # Get the token from the request
        token = request.args.get('token')

        # Find the EPV record
        epv = EPV.query.filter_by(epv_id=epv_id).first()
        if not epv:
            return render_template('error.html', error="EPV record not found"), 404

        # Find the approval record if token is provided
        approval = None
        approver_email = request.args.get('email', 'Unknown')

        if token:
            # Find the approval record by token
            from models import EPVApproval
            approval = EPVApproval.query.filter_by(epv_id=epv.id, token=token).first()

            if approval:
                # Check if the approver has already taken action
                if approval.status != 'pending':
                    return render_template('error.html',
                                          error="You have already {0} this expense.".format(approval.status),
                                          message="You cannot change your decision once submitted."), 400

                # Update the approval record
                approval.status = 'approved'
                approval.action_date = datetime.now()
                approval.comments = request.args.get('comments', '')
                approver_email = approval.approver_email
            else:
                return render_template('error.html', error="Invalid approval token"), 400

        # Update the legacy fields for backward compatibility
        epv.approved_by = approver_email
        epv.approved_on = datetime.now()

        # Check if all approvers have approved
        all_approved = True
        any_rejected = False

        # Get all approval records for this EPV
        from models import EPVApproval
        approvals = EPVApproval.query.filter_by(epv_id=epv.id).all()

        for appr in approvals:
            if appr.status == 'rejected':
                any_rejected = True
                break
            elif appr.status != 'approved':
                all_approved = False

        # Update the EPV status based on approval status
        if any_rejected:
            epv.status = 'rejected'
        elif all_approved and len(approvals) > 0:
            epv.status = 'approved'
        else:
            epv.status = 'partially_approved'

        db.session.commit()

        # Render a success page
        return render_template('approval_result.html',
                              result="approved",
                              epv=epv,
                              message="The expense has been approved successfully.")

    except Exception as e:
        print(f"Error approving expense: {str(e)}")
        return render_template('error.html', error=f"An error occurred: {str(e)}"), 500

# Route to show rejection form
@app.route('/reject-expense/<epv_id>')
def reject_expense(epv_id):
    try:
        # Get the token from the request
        token = request.args.get('token')

        # Find the EPV record
        epv = EPV.query.filter_by(epv_id=epv_id).first()
        if not epv:
            return render_template('error.html', error="EPV record not found"), 404

        # Find the approval record if token is provided
        approval = None
        approver_email = request.args.get('email', 'Unknown')

        if token:
            # Find the approval record by token
            from models import EPVApproval
            approval = EPVApproval.query.filter_by(epv_id=epv.id, token=token).first()

            if approval:
                # Check if the approver has already taken action
                if approval.status != 'pending':
                    return render_template('error.html',
                                          error="You have already {0} this expense.".format(approval.status),
                                          message="You cannot change your decision once submitted."), 400

                # Show the rejection form
                try:
                    return render_template('rejection_form.html',
                                          epv=epv,
                                          token=token,
                                          approver_email=approval.approver_email)
                except Exception as template_error:
                    print(f"Template error: {str(template_error)}")
                    # Fallback to a simpler form if there's a template error
                    return render_template('error.html',
                                          error="Please provide a reason for rejection",
                                          message=f"<form action='{url_for('process_rejection', epv_id=epv_id)}' method='POST'>"
                                                  f"<input type='hidden' name='token' value='{token}'>"
                                                  f"<input type='hidden' name='email' value='{approval.approver_email}'>"
                                                  f"<div class='mb-3'><label for='reason'>Reason:</label>"
                                                  f"<textarea name='reason' id='reason' rows='4' class='form-control' required></textarea></div>"
                                                  f"<button type='submit' class='btn btn-danger'>Reject</button></form>")
            else:
                return render_template('error.html', error="Invalid rejection token"), 400

        # If no token, show the rejection form with the provided email
        try:
            return render_template('rejection_form.html',
                                  epv=epv,
                                  token=token,
                                  approver_email=approver_email)
        except Exception as template_error:
            print(f"Template error: {str(template_error)}")
            # Fallback to a simpler form if there's a template error
            return render_template('error.html',
                                  error="Please provide a reason for rejection",
                                  message=f"<form action='{url_for('process_rejection', epv_id=epv_id)}' method='POST'>"
                                          f"<input type='hidden' name='email' value='{approver_email}'>"
                                          f"<div class='mb-3'><label for='reason'>Reason:</label>"
                                          f"<textarea name='reason' id='reason' rows='4' class='form-control' required></textarea></div>"
                                          f"<button type='submit' class='btn btn-danger'>Reject</button></form>")

    except Exception as e:
        print(f"Error showing rejection form: {str(e)}")
        return render_template('error.html', error=f"An error occurred: {str(e)}"), 500

# Route to process rejection
@app.route('/process-rejection/<epv_id>', methods=['POST'])
def process_rejection(epv_id):
    try:
        # Get form data
        token = request.form.get('token')
        approver_email = request.form.get('email', 'Unknown')
        rejection_reason = request.form.get('reason', '')

        # Validate rejection reason
        if not rejection_reason:
            return render_template('error.html',
                                  error="Rejection reason is required",
                                  message="Please provide a reason for rejecting this expense."), 400

        # Find the EPV record
        epv = EPV.query.filter_by(epv_id=epv_id).first()
        if not epv:
            return render_template('error.html', error="EPV record not found"), 404

        # Find the approval record if token is provided
        approval = None

        print(f"DEBUG: Rejection reason: {rejection_reason}")

        if token:
            # Find the approval record by token
            from models import EPVApproval
            approval = EPVApproval.query.filter_by(epv_id=epv.id, token=token).first()

            if approval:
                # Check if the approver has already taken action
                if approval.status != 'pending':
                    return render_template('error.html',
                                          error="You have already {0} this expense.".format(approval.status),
                                          message="You cannot change your decision once submitted."), 400

                # Update the approval record
                approval.status = 'rejected'
                approval.action_date = datetime.now()
                approval.comments = rejection_reason
                approver_email = approval.approver_email
            else:
                return render_template('error.html', error="Invalid rejection token"), 400

        # Update the legacy fields for backward compatibility
        epv.rejected_by = approver_email
        epv.rejected_on = datetime.now()
        epv.rejection_reason = rejection_reason

        # If any approver rejects, the entire EPV is rejected
        epv.status = 'rejected'

        db.session.commit()

        # Render a success page
        return render_template('approval_result.html',
                              result="rejected",
                              epv=epv,
                              message="The expense has been rejected.")

    except Exception as e:
        print(f"Error rejecting expense: {str(e)}")
        return render_template('error.html', error=f"An error occurred: {str(e)}"), 500

# Route to view a specific EPV record
@app.route('/epv-record/<epv_id>')
def view_epv_record(epv_id):
    try:
        # Get the token from the request
        token = request.args.get('token')

        # Find the EPV record
        epv = EPV.query.filter_by(epv_id=epv_id).first()
        if not epv:
            return render_template('error.html', error="EPV record not found"), 404

        # Get EPV items
        epv_items = EPVItem.query.filter_by(epv_id=epv.id).all()

        # Get approval records
        from models import EPVApproval
        approvals = EPVApproval.query.filter_by(epv_id=epv.id).all()

        # Check if the user is an approver with a valid token
        is_approver = False
        current_approval = None

        if token:
            current_approval = EPVApproval.query.filter_by(epv_id=epv.id, token=token).first()
            if current_approval:
                is_approver = True

        # Render the EPV record view
        return render_template('epv_record_view.html',
                              epv=epv,
                              epv_items=epv_items,
                              approvals=approvals,
                              is_approver=is_approver,
                              current_approval=current_approval,
                              token=token)

    except Exception as e:
        print(f"Error viewing EPV record: {str(e)}")
        return render_template('error.html', error=f"An error occurred: {str(e)}"), 500

# Route to view all EPV records
@app.route('/epv-records')
def epv_records():
    # Check if user is logged in
    if 'email' not in session:
        print("DEBUG: User not logged in, redirecting to login")
        return redirect(url_for('login', next='/epv-records'))

    print(f"DEBUG: EPV Records accessed by {session.get('email')}")
    print(f"DEBUG: Session data: {session}")

    # Get the user's role
    user_email = session.get('email')
    employee = EmployeeDetails.query.filter_by(email=user_email).first()
    role = employee.role if employee else 'user'

    # Get EPV records based on role
    if role == 'Super Admin':
        # Super admins can see all records
        records = EPV.query.order_by(EPV.submission_date.desc()).all()
    else:
        # Regular users and admins can only see their own records
        records = EPV.query.filter_by(email_id=user_email).order_by(EPV.submission_date.desc()).all()

    # Debug output
    print(f"DEBUG: User role: {role}")
    print(f"DEBUG: Found {len(records)} EPV records")
    for record in records:
        print(f"DEBUG: EPV ID: {record.epv_id}, Employee: {record.employee_name}, Email: {record.email_id}, Status: {record.status}")

    # Return the EPV records template
    print("DEBUG: Rendering epv_records.html template")
    try:
        return render_template('epv_records.html', records=records)
    except Exception as e:
        print(f"DEBUG: Error rendering template: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return f"Error: {str(e)}", 500

# Route to view a specific EPV record
@app.route('/epv-record/<epv_id>')
def epv_record(epv_id):
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))

    # Get the user's role
    user_email = session.get('email')
    employee = EmployeeDetails.query.filter_by(email=user_email).first()
    role = employee.role if employee else 'user'

    # Get the EPV record
    record = EPV.query.filter_by(epv_id=epv_id).first_or_404()

    # Check if the user has permission to view this record
    if role != 'Super Admin' and record.email_id != user_email:
        print(f"DEBUG: Access denied for user {user_email} to view EPV {epv_id}")
        return redirect(url_for('epv_records'))

    # Get the expense items for this EPV
    items = EPVItem.query.filter_by(epv_id=record.id).all()

    print(f"DEBUG: User {user_email} viewing EPV record {epv_id}")
    return render_template('epv_record.html', record=record, items=items)

if __name__ == '__main__':
    # Allow OAuth without HTTPS for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Print debug information
    print("DEBUG: Starting application with the following configuration:")
    print(f"DEBUG: GOOGLE_CLIENT_ID: {os.environ.get('GOOGLE_CLIENT_ID')}")
    print(f"DEBUG: OAUTHLIB_INSECURE_TRANSPORT: {os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')}")

    # Initialize the database
    with app.app_context():
        # Don't drop all tables to preserve EPV records
        # db.drop_all()
        db.create_all()
        init_db(app)

    # Always use port 5000 for Google OAuth to work correctly
    app.run(host='127.0.0.1', port=5000, debug=True)
