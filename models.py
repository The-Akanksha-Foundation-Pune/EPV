from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from datetime import datetime

db = SQLAlchemy()

class CostCenter(db.Model):
    __tablename__ = 'costcenter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    costcenter = db.Column(db.String(100), nullable=False)
    approver_email = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    drive_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<CostCenter {self.costcenter}>'

class EmployeeDetails(db.Model):
    __tablename__ = 'employee_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), nullable=True)
    manager = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<EmployeeDetails {self.name} ({self.email})>'

class SettingsFinance(db.Model):
    __tablename__ = 'settings_finance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setting_name = db.Column(db.String(100), nullable=False, unique=True)
    setting_value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    parent_drive_folder = db.Column(db.String(100), nullable=True)
    parent_drive_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<SettingsFinance {self.setting_name}: {self.setting_value}>'

class ExpenseHead(db.Model):
    __tablename__ = 'expense_head'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    head_name = db.Column(db.String(100), nullable=False)
    head_code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ExpenseHead {self.head_name} ({self.head_code})>'

class EPV(db.Model):
    """
    Model to store all expense voucher data
    """
    __tablename__ = 'epv'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.String(30), unique=True, nullable=False)  # EPV-YYYYMMDD-XXXXXXXXXX format

    # Employee details
    email_id = db.Column(db.String(100), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False)

    # Date range
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)

    # Payment and acknowledgement
    payment_to = db.Column(db.String(100), nullable=False)  # Previously expense_type
    acknowledgement = db.Column(db.String(255))  # For any acknowledgement information

    # Metadata
    submission_date = db.Column(db.DateTime, default=datetime.now)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"

    # Cost center
    cost_center_id = db.Column(db.Integer, db.ForeignKey('costcenter.id'))
    cost_center = db.relationship('CostCenter', backref=db.backref('expenses', lazy=True))
    cost_center_name = db.Column(db.String(100), nullable=False)

    # File storage details
    file_url = db.Column(db.String(255))  # URL to access the file in Google Drive
    drive_file_id = db.Column(db.String(100))  # Google Drive file ID

    # Financial details
    total_amount = db.Column(db.Float, nullable=False)
    amount_in_words = db.Column(db.String(255))

    # Approval workflow
    status = db.Column(db.String(20), default='submitted')  # submitted, pending_approval, approved, rejected, partially_approved
    # The overall status is determined by the individual approver statuses in EPVApproval
    # If all approvers approve, status = 'approved'
    # If any approver rejects, status = 'rejected'
    # If some approve and none reject, status = 'partially_approved'

    # Legacy fields (kept for backward compatibility)
    approver_emails = db.Column(db.Text)  # Comma-separated list of approver emails
    approved_by = db.Column(db.String(100))  # Email of the approver
    approved_on = db.Column(db.DateTime)  # When it was approved
    rejected_by = db.Column(db.String(100))  # Email of the person who rejected
    rejected_on = db.Column(db.DateTime)  # When it was rejected
    rejection_reason = db.Column(db.Text)  # Why it was rejected

    def __repr__(self):
        return f"<EPV {self.epv_id}>"

class EPVApproval(db.Model):
    """
    Model to store approval status for each approver of an EPV
    """
    __tablename__ = 'epv_approval'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('approvals', lazy=True))

    # Approver details
    approver_email = db.Column(db.String(100), nullable=False)
    approver_name = db.Column(db.String(100))

    # Approval status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    action_date = db.Column(db.DateTime)  # When the approver took action
    comments = db.Column(db.Text)  # Any comments from the approver

    # Token for secure approval/rejection links
    token = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f"<EPVApproval {self.id} for EPV {self.epv_id} by {self.approver_email}>"

class EPVItem(db.Model):
    """
    Model to store individual expense items within an EPV
    """
    __tablename__ = 'epv_item'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('items', lazy=True))

    # Expense details
    expense_invoice_date = db.Column(db.Date, nullable=False)  # Renamed from invoice_date
    expense_head = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Financial details
    gst = db.Column(db.Float, default=0.0)  # GST amount or percentage
    amount = db.Column(db.Float, nullable=False)

    # Receipt details
    receipt_filename = db.Column(db.String(255))
    receipt_path = db.Column(db.String(255))
    receipt_drive_id = db.Column(db.String(100))

    def __repr__(self):
        return f"<EPVItem {self.id} for EPV {self.epv_id}>"

# Function to initialize the database
def init_db(app):
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()

        print("Database initialized with all tables.")

        inspector = inspect(db.engine)

        # Initialize cost centers if the table is empty
        if not inspector.has_table('costcenter') or CostCenter.query.count() == 0:
            # List of cost centers to add
            cost_centers = [
                "SBP_BP",
                "SBP_Moshi",
                "PKGEMS",
                "ANWEMS",
                "LDRKEMS",
                "LAPMEMS",
                "KCTVN",
                "CSMEMS",
                "BOPEMS",
                "MEMS",
                "Late Baburaoji Bobade NMCPS",
                "Late Gopalrao Moghare (Khadan)",
                "Ramnagar NMCPS (Nagpur)",
                "Rani Durgavati NMCPS (Nagpur)",
                "Rambhau Mhalginagar NMCPS",
                "Babhulban NMCPS (Nagpur)",
                "PE - Pune",
                "NST - Instruction Specialist - Pune",
                "Counselling & Intervention Pune",
                "Operations Pune",
                "NST - Coaches - Nagpur",
                "NST - Coaches - Pune",
                "Operations Nagpur",
                "PE - Nagpur",
                "Counselling & Intervention Nagpur",
                "NST - Instruction Specialist - Nagpur",
                "Community Engagement Pune",
                "Community Engagement Nagpur",
                "Digital Literacy",
                "Vocational Labs",
                "Sports Program",
                "School Management System",
                "CSMEMS learning tour",
                "Knowledge management",
                "Alumni Management System",
                "IT & Tech Infra - SETU",
                "Leads Development & Training",
                "SBP - Government School (Maharashtra)",
                "Student Wellbeing COI Leads",
                "Scholarship - Pune",
                "IT & Tech Infra - MSP",
                "ASE Pune",
                "Art for Akanksha",
                "IT & Tech Infra - ASE",
                "IT & Tech Infra - Admin",
                "Management - CEO",
                "Management - COO",
                "Impact & Research",
                "Donor Relations & Communication",
                "Finance - Central",
                "Central Administration",
                "Human Resources Central",
                "Project Rise",
                "ABC"
            ]

            # Add default city values based on name
            for cc in cost_centers:
                city = "Pune"  # Default city
                if "Nagpur" in cc:
                    city = "Nagpur"

                # Add drive IDs for specific cost centers
                drive_id = None
                if cc == "SBP_BP":
                    drive_id = "1Ku7ai51N19-p3nYViAa1eeooQjWPRUN1"
                elif cc == "KCTVN":
                    drive_id = "1w48U4Kv_zZUhf9-Bwx6df8su8vQEqKvV"

                # Create and add the cost center to the database
                cost_center = CostCenter(costcenter=cc, city=city, drive_id=drive_id)
                db.session.add(cost_center)

            # Commit the changes
            db.session.commit()
            print("Database initialized with cost centers.")

        # Initialize employee details if the table is empty
        print("DEBUG: Checking employee_details table...")
        if not inspector.has_table('employee_details'):
            print("DEBUG: employee_details table does not exist, creating it...")
        elif EmployeeDetails.query.count() == 0:
            print("DEBUG: employee_details table exists but is empty, populating it...")
        else:
            print(f"DEBUG: employee_details table exists and has {EmployeeDetails.query.count()} records.")

        if not inspector.has_table('employee_details') or EmployeeDetails.query.count() == 0:
            # Employee data from the Google Sheet
            employees = [
                {"email": "nikhil.aher@akanksha.org", "employee_id": "NIKAHE160185", "manager": "3df.demo@akanksha.org", "name": "Nikhil Aher", "role": "admin"},
                {"email": "anil.naik@akanksha.org", "employee_id": "CHAAHE", "manager": "fatima.sawant@akanksha.org", "name": "Chaitrali Aher", "role": "Central"},
                {"email": "amit.kashid@akanksha.org", "employee_id": "SHAPAT", "manager": "shruti.das@akanksha.org", "name": "Sharad", "role": "Super Admin"},
                {"email": "shubham.ambolikar@akanksha.org", "employee_id": "MAYGAnJ", "manager": "anchal.wasnik@akanksha.org", "name": "mayur", "role": "Mumbai_FInance"},
                {"email": "ajay.hendre@akanksha.org", "employee_id": "TriDHha1112", "manager": "sushma.pathare@akanksha.org", "name": "Triveni Dhamdhere", "role": "Pune_Finance"},
                {"email": "pramod.giri@akanksha.org", "employee_id": "", "manager": "parijat.prakash@akanksha.org", "name": "", "role": ""},
                {"email": "rebecca.kamble@akanksha.org", "employee_id": "", "manager": "parijat.prakash@akanksha.org", "name": "", "role": ""},
                {"email": "ashwini.mayekar@akanksha.org", "employee_id": "", "manager": "samina.quettawala@akanksha.org", "name": "", "role": ""},
                {"email": "shraddha.morgaonkar@akanksha.org", "employee_id": "", "manager": "shalini.sachdev@akanksha.org", "name": "", "role": ""},
                {"email": "ajay.sonawane@akanksha.org", "employee_id": "", "manager": "shruti.manerker@akanksha.org", "name": "", "role": ""},
                {"email": "kiran.deogadkar@akanksha.org", "employee_id": "", "manager": "shivani.yadav@akanksha.org", "name": "", "role": ""},
                {"email": "rekha.kolsure@akanksha.org", "employee_id": "", "manager": "ritu.pasricha@akanksha.org", "name": "", "role": ""},
                {"email": "priyanka.pachpor@akanksha.org", "employee_id": "", "manager": "Simranjeet.sankat@akanksha.org", "name": "", "role": ""},
                {"email": "aniket.mayekar@akanksha.org", "employee_id": "", "manager": "prachi.mangaonkar@akanksha.org", "name": "", "role": ""},
                {"email": "rohit.talegaonkar@akanksha.org", "employee_id": "", "manager": "nilambari.nair@akanksha.org", "name": "", "role": ""},
                {"email": "pramod.kamble@akanksha.org", "employee_id": "", "manager": "sima.jhaveri@akanksha.org", "name": "", "role": ""},
                {"email": "aishwarya.mestry@akanksha.org", "employee_id": "", "manager": "bhima.jetty@akanksha.org", "name": "", "role": ""},
                {"email": "sushil.joharkar@akanksha.org", "employee_id": "", "manager": "diana.isabel@akanksha.org", "name": "", "role": ""},
                {"email": "santosh.shirwadkar@akanksha.org", "employee_id": "", "manager": "alsana.lakdawala@akanksha.org", "name": "", "role": ""},
                {"email": "suyash.modak@akanksha.org", "employee_id": "", "manager": "nishant.singhania@akanksha.org", "name": "", "role": ""},
                {"email": "lalit.barapatre@akanksha.org", "employee_id": "", "manager": "mamta.sylvester@akanksha.org", "name": "", "role": ""},
                {"email": "chetan.telang@akanksha.org", "employee_id": "", "manager": "harshada.jadhav@akanksha.og", "name": "", "role": ""},
                {"email": "vishnu.hiwale@akanksha.org", "employee_id": "", "manager": "harshada.jadhav@akanksha.org", "name": "", "role": ""},
                {"email": "sunil.kamble@akanksha.org", "employee_id": "", "manager": "mohmmed.ahmedulla@akanksha.org", "name": "", "role": ""},
                {"email": "umesh.shejul@akanksha.org", "employee_id": "", "manager": "merlin1.elias@akanksha.org", "name": "", "role": ""},
                {"email": "Sushant.kesarkar@akanksha.org", "employee_id": "", "manager": "mandira.purohit@akanksha.org", "name": "", "role": ""},
                {"email": "ankita.dawal@akanksha.org", "employee_id": "", "manager": "sakshi.bhatia@akanksha.org", "name": "", "role": ""},
                {"email": "prakash.dhangar@akanksha.org", "employee_id": "", "manager": "prachi.sanghvi@akanksha.org", "name": "", "role": ""}
            ]

            # Add employees to the database
            for emp_data in employees:
                # Convert email to lowercase for consistency
                employee = EmployeeDetails(
                    email=emp_data["email"].lower(),
                    employee_id=emp_data["employee_id"],
                    manager=emp_data["manager"].lower() if emp_data["manager"] else None,
                    name=emp_data["name"],
                    role=emp_data["role"]
                )
                db.session.add(employee)

            # Commit the changes
            db.session.commit()
            print("Database initialized with employee details.")

        # Initialize finance settings if the table is empty
        print("DEBUG: Checking settings_finance table...")
        if not inspector.has_table('settings_finance'):
            print("DEBUG: settings_finance table does not exist, creating it...")
        elif SettingsFinance.query.count() == 0:
            print("DEBUG: settings_finance table exists but is empty, populating it...")
        else:
            print(f"DEBUG: settings_finance table exists and has {SettingsFinance.query.count()} records.")

        if not inspector.has_table('settings_finance') or SettingsFinance.query.count() == 0:
            # Finance settings
            settings = [
                {
                    "setting_name": "max_days_past",
                    "setting_value": "30",
                    "description": "Maximum number of days in the past for expense claims",
                    "parent_drive_folder": "SBP_BP",
                    "parent_drive_id": "1Ku7ai51N19-p3nYViAa1eeooQjWPRUN1"
                },
                {
                    "setting_name": "drive_folder_kctvn",
                    "setting_value": "KCTVN",
                    "description": "Google Drive folder for KCTVN",
                    "parent_drive_folder": "KCTVN",
                    "parent_drive_id": "1w48U4Kv_zZUhf9-Bwx6df8su8vQEqKvV"
                }
            ]

            # Add settings to the database
            for setting_data in settings:
                setting = SettingsFinance(
                    setting_name=setting_data["setting_name"],
                    setting_value=setting_data["setting_value"],
                    description=setting_data["description"],
                    parent_drive_folder=setting_data["parent_drive_folder"],
                    parent_drive_id=setting_data["parent_drive_id"]
                )
                db.session.add(setting)

            # Commit the changes
            db.session.commit()
            print("Database initialized with finance settings.")

        # Initialize expense heads if the table is empty
        print("DEBUG: Checking expense_head table...")
        if not inspector.has_table('expense_head'):
            print("DEBUG: expense_head table does not exist, creating it...")
        elif ExpenseHead.query.count() == 0:
            print("DEBUG: expense_head table exists but is empty, populating it...")
        else:
            print(f"DEBUG: expense_head table exists and has {ExpenseHead.query.count()} records.")

        if not inspector.has_table('expense_head') or ExpenseHead.query.count() == 0:
            # Expense head data from the Google Sheet
            expense_heads = [
                {"head_name": "Travel", "head_code": "TRV", "description": "Travel expenses including airfare, train, bus, etc.", "is_active": True},
                {"head_name": "Accommodation", "head_code": "ACC", "description": "Hotel and lodging expenses", "is_active": True},
                {"head_name": "Meals", "head_code": "MEL", "description": "Food and beverage expenses during business trips", "is_active": True},
                {"head_name": "Office Supplies", "head_code": "OFF", "description": "Stationery, printer ink, and other office consumables", "is_active": True},
                {"head_name": "Communication", "head_code": "COM", "description": "Phone bills, internet charges, and other communication expenses", "is_active": True},
                {"head_name": "Training", "head_code": "TRN", "description": "Costs related to workshops, seminars, and professional development", "is_active": True},
                {"head_name": "Equipment", "head_code": "EQP", "description": "Purchase or rental of equipment and hardware", "is_active": True},
                {"head_name": "Software", "head_code": "SFT", "description": "Software licenses and subscriptions", "is_active": True},
                {"head_name": "Miscellaneous", "head_code": "MSC", "description": "Other expenses that don't fit into specific categories", "is_active": True},
                {"head_name": "Transportation", "head_code": "TRN", "description": "Local transportation like taxis, buses, and fuel", "is_active": True}
            ]

            # Add expense heads to the database
            for head_data in expense_heads:
                expense_head = ExpenseHead(
                    head_name=head_data["head_name"],
                    head_code=head_data["head_code"],
                    description=head_data["description"],
                    is_active=head_data["is_active"]
                )
                db.session.add(expense_head)

            # Commit the changes
            db.session.commit()
            print("Database initialized with expense heads.")
