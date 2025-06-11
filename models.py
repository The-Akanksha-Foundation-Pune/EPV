from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from datetime import datetime
from flask_login import UserMixin
# Removed OAuth imports since we're not using OAuth storage anymore

db = SQLAlchemy()

class CostCenter(db.Model):
    __tablename__ = 'costcenter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    costcenter = db.Column(db.String(100), nullable=False, index=True)
    approver_email = db.Column(db.String(100), nullable=True, index=True)  # Email of the cost center approver/administrator
    city = db.Column(db.String(50), nullable=True, index=True)
    drive_id = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __repr__(self):
        return f'<CostCenter {self.costcenter}>'

    @staticmethod
    def get_default_cost_centers():
        """Return the default cost center data for initialization"""
        return [
            ("Abhyudaya Nagar", "fatima.sawant@akanksha.org", "Mumbai", "1riw8YcNK2AbkdUcHQOBIaOsu5XsimPAg", True),
            ("AFA Sales", "ruchika.gupta@akanksha.org", "", "1Ad49VZ1E6oA9YMVrD-RYTR3dDReP0TKE", True),
            ("ANWEMS", "shruti.das@akanksha.org", "Pune", "1JTgrRBu54yJwkgFUqou2BzygeJSYLZhB", True),
            ("Art Curriculum in Schools", "ruchika.gupta@akanksha.org", "", "136488itBUyzAKeo_WqS779yKWAqNZrGy", True),
            ("ASE Mumbai", "zoya.khan@akanksha.org", "Mumbai", "1zzJg1C_ii773ZjvuUo7f-NbE0qcmCmMt", True),
            ("ASE Pune", "zoya.khan@akanksha.org", "", "1fsCtoTj95L05hByqhkvBDoWdPNw9uagy", True),
            ("Aspiring Teachers", "venil.ali@akanksha.org", "", "1C9LOdnIJOvsZNXeuxP83wKoP8blXgpuI", True),
            ("Babhulban NMCPS (Nagpur)", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1mNIOjhowfdDJEEnHPo3IcY5lxxSkGO-f", True),
            ("BOPEMS", "sushma.pathare@akanksha.org", "Pune", "1Z7MxiicescNuEd5okbndzUl3j-0FHM0w", True),
            ("Central Administration", "megha.agarwal@akanksha.org/anjali.suresh@akanksha.org", "", "1tfBBT488oTrHopRPTFj82Qsx8SBRd3t-", True),
            ("Chief of School and Alumni (COSA)", "venil.ali@akanksha.org", "", "1IQR5ze3QhShTnQyz4QGwAtnIpP-s53j6", True),
            ("Coaches - Mumbai", "sheetal.murudkar@akanksha.org", "Mumbai", "1kKvpLxLDRNpoB7sFT21OkBm3jADQCUTo", True),
            ("Coaches - Nagpur", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1dtT5SEZrA_UvyM2NCJ7KxJZ-GT_28_my", True),
            ("Coaches - Pune", "sivakami.kotla@akanksha.org", "Pune", "1atuB34p_wlFJgLJ1aCvz-DOuuR3R8jMp", True),
            ("Communication", "urvashi.pant@akanksha.org", "", "1SwzQDm44JhvZeU_16-TWiWjqGB8P2AGe", True),
            ("Community Engagement Mumbai", "sheetal.murudkar@akanksha.org", "Mumbai", "1fyyOyUcsOg6-_-EOs2eOD_knfv6TDgXU", True),
            ("Community Engagement Nagpur", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1s2k5NJbDGjZqDP6KbJPemTFVC60QLOX6", True),
            ("Community Engagement Pune", "sivakami.kotla@akanksha.org", "Pune", "1wVqR55aw8d5SJebVgIpSj5ovyhs_zzaF", True),
            ("Counseling & Intervention Mumbai", "sheetal.murudkar@akanksha.org", "Mumbai", "1DVMKGA9CT_TyBoaBTaAa2Vq_a7lzolhT", True),
            ("Counseling & Intervention Nagpur", "somsuvra.chatterjee@akanksha.org", "Nagpur", "h1ZRxl_zcqLI1LWO1b98gRcKOeeWazD1ki", True),
            ("Counseling & Intervention Pune", "sivakami.kotla@akanksha.org", "Pune", "1GrqDvaTAkJaRHVtiHrmqP1G-jywj_jGe", True),
            ("CSMEMS", "parijat.prakash@akanksha.org", "Pune", "1cTVu0RyHdHJyS33_r4_Ekpl4ZKOSwyeb", True),
            ("CWSN - IS", "venil.ali@akanksha.org", "", "19ZDT9EfcTPGctC4H7FEbgB7tGcRRGFnB", True),
            ("D. N. Nagar", "samina.quettawala@akanksha.org", "Mumbai", "1bqaMJzz8wpRu-tLpMSbJhR3unVJVde1p", True),
            ("Digital Learning", "gauri.kirtane@akanksha.org", "", "1CT0pIDNgPFfnSTYiinfGRR-v2s7Ans_C", True),
            ("Donor Relations", "chanda.peswani@akanksha.org", "", "1NMB2bZOuSbITIBg0-MmnoEoSl_k-2VFp", True),
            ("Finance - Central", "manoj.balamkar@akanksha.org", "", "19_4f_SjMLNPazQI-Ka-l7t_6YsLYx75r", True),
            ("Global Awareness Initiative", "sivakami.kotla@akanksha.org", "", "1GQKKYxVq_PapWRxbO491kbFdNWu7xjCg", True),
            ("Human Resources Central", "megha.agarwal@akanksha.org", "", "1p3ZaEOyV8p2va2ChSwD7FUcWUZKCpBSZ", True),
            ("Impact & Research", "nishant.singhania@akanksha.org", "", "1_zpOwQA9o68SAEOdPip04CwCa4pXdgno", True),
            ("Instruction Specialist", "gauri.kirtane@akanksha.org", "", "1lDtc0jODzZYmAK1U1_et9kcHCtFLQleC", True),
            ("Instruction Specialist - Mumbai", "gauri.kirtane@akanksha.org", "Mumbai", "1rQ9p6JWe2bSwChZ3xZ5WhS8EcmnecIHE", True),
            ("Instruction Specialist - Nagpur", "gauri.kirtane@akanksha.org", "Nagpur", "1LNjq5q2nvTVSn6NNh368N5jcvrEAPqah", True),
            ("Instruction Specialist - Pune", "gauri.kirtane@akanksha.org", "Pune", "1FHSRoksFPXZXtLMSUA2jQWHSlQ122Ulr", True),
            ("IT & Tech Infra - Admin", "nitin.aurora@akanksha.org", "", "1YRKFMPz_TuS2VHLXTQbYTL005pthPtZ-", True),
            ("IT & Tech Infra - ASE", "nitin.aurora@akanksha.org", "", "1nJ1EnHitWsGv_uxwjgTVRuvdh9DHD_BT", True),
            ("IT & Tech Infra - MSP", "nitin.aurora@akanksha.org", "", "1fVBNssVbcrQKmUQNqzSLV-5h0oj43CpL", True),
            ("KCTVN", "shalini.sachdev@akanksha.org", "Pune", "15Li69dovMhLaUo96Z8dX6DpDKjjfxh_T", True),
            ("LAPMEMS", "shruti.manerker@akanksha.org", "Pune", "1Y6s8dTIrTSql0n--e5Tf_QjNStPA6oVD", True),
            ("Late Baburaoji Bobade NMCPS", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1qe6vQLM7HSxypG31RRECq28kqXiTf4Gv", True),
            ("Late Gopalrao Moghare (Khadan)", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1DVmjbr9NdNTISYyJKg6VrJQ8qeFrOwvR", True),
            ("Laxmi Nagar", "prachi.mangaonkar@akanksha.org", "Mumbai", "1sF2cj6clLsLH_H1aAQftL163U1vUet8L", True),
            ("LDRKEMS", "ritu.pasricha@akanksha.org", "Pune", "1WUmQ5SzjgyM848WKXNDD0JrFtl-Zc-A_", True),
            ("Mahalaxmi", "sima.jhaveri@akanksha.org", "Mumbai", "1HPLJAbfzsoA2M8dUCanSGhREW3Lo67OX", True),
            ("Management - CEO", "saurabh.taneja@akanksha.org", "", "1DrVccC0H2iEX65zK-pd1fJDn65EtnZY6", True),
            ("MEMS", "nilambari.nair@akanksha.org", "Pune", "1Egnob_v9nXb5uvO15CR7or65W3fpAR2f", True),
            ("MPMMPS", "bhima.jetty@akanksha.org", "Mumbai", "1JaU9IhNJE-jNpQJv6sJ4qzo2wHSKH0Iz", True),
            ("Natwar Nagar", "rekha.ghelani@akanksha.org", "Mumbai", "1f46qyK_qTV34rydMX4pFnmQOnwj-hAH7", True),
            ("Navi Mumbai", "diana.isabel@akanksha.org", "Mumbai", "12FNpfiRUVOAtGdnX5iA204XpaSdrOWU7", True),
            ("Operations Mumbai", "sheetal.murudkar@akanksha.org", "Mumbai", "13RX8hKfusoKIyF1Ab1iPu7JTemRx87E-", True),
            ("Operations Nagpur", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1OWdy60tQrxhq6i1o1aagRbIWf2mFw-E1", True),
            ("Operations Pune", "sivakami.kotla@akanksha.org", "Pune", "1NRMF4Dq78w0COEcMlNw-kCH0QkEtdrHR", True),
            ("PE Mumbai", "subhash.ghodake@akanksha.org", "Mumbai", "1JOqgHo0OePrAHzNRvtZMiXzv4YygRJgb", True),
            ("PE Nagpur", "gauri.kirtane@akanksha.org", "Nagpur", "1UyU5JredtHqZL28Eyx7dAM2D8fs1fSnH", True),
            ("PE Pune", "sivakami.kotla@akanksha.org", "Pune", "1wzh84o_0dgdaX7lnL9_Yhe7siSej-JTR", True),
            ("PKGEMS", "nishant.singhania@akanksha.org", "Pune", "1xl8FfP7SOqecpQBF5mYYBoZN2ZBI74wB", True),
            ("Rambhau Mhalginagar NMCPS", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1YxJEV5xtS-7NYboLFGmIYafcE1CqTwtu", True),
            ("Ramnagar NMCPS (Nagpur)", "somsuvra.chatterjee@akanksha.org", "Nagpur", "1JJ_j7adnRicZOcK4ItYhTjUjLsrbDBNW", True),
            ("Rani Durgavati NMCPS (Nagpur)", "somsuvra.chatterjee@akanksha.org", "Nagpur", "103dt8_Zhkz2sVMdj0YLSWxOtLz6rSOTy", True),
            ("RISE", "sapna1.shah@akanksha.org", "", "1Enm2IcW99TASUN3VqftmmHNltN-XlRTk", True),
            ("SBPEMS - Bhawani Peth", "mohmmed.ahmedulla@akanksha.org", "Pune", "1Zmo8zq6viyAwxiaH3QGyuUG9TlEqE63t", True),
            ("SBPEMS - Moshi", "merlin1.elias@akanksha.org", "Pune", "1G_tN9rDJfGqPV4HXbWWoDhU23KCkwLC5", True),
            ("Scholarship - Mumbai", "zoya.khan@akanksha.org", "Mumbai", "1s9h8ZizfAmEMdhORLfA3ADRkuTuJHXrJ", True),
            ("Scholarship - Pune", "zoya.khan@akanksha.org", "Pune", "13TKF2LI7TwzWPoj3m91COhQ8LC_jvAd1", True),
            ("Senior Secondary Specialist", "gauri.kirtane@akanksha.org", "", "12CV5MZgALWp-5f2KtXigPc0S8tgDBQzF", True),
            ("SETU", "jayshree.oberoi@akanksha.org", "Pune", "18Y8yc1IdGGZIGbfLdfqPQ_ksMyEf25vU", True),
            ("Setu - Art", "jayshree.oberoi@akanksha.org", "", "1q-syD2OYNac-TEo4Z_h3az-TRbqSL0vN", True),
            ("Shindewadi", "sakshi.bhatia@akanksha.org", "Mumbai", "1xjagICZtuhH4Oj5kA15NRrCd-CE9b2rD", True),
            ("Sitaram Mill", "mandira.purohit@akanksha.org", "Mumbai", "1_EvNrCm3vEn_zPlfS2vVT1XQfbbNdzd6", True),
            ("SL Academy", "venil.ali@akanksha.org", "", "1dko5lsmLrlyTGvbSFbtmzPmW_6J0jWPD", True),
            ("Sports Program Mumbai", "subhash.ghodake@akanksha.org", "Mumbai", "1SckHL7C8NQS4AfZWKRvF1cfXdFIWJ2z3", True),
            ("Sports Program Nagpur", "subhash.ghodake@akanksha.org", "Nagpur", "1ptib4zUhy4-fj6Hjzwzkh3BMPUUOaFxU", True),
            ("Sports Program Pune", "subhash.ghodake@akanksha.org", "Pune", "1Kii9qi9zz5cpo5SrTYe6wdwXUxfVWyFI", True),
            ("STEM", "zoya.khan@akanksha.org", "", "14BSwzTyMODo9_2fMSg_asBlcyw9V-jSb", True),
            ("Student Wellbeing COI Leads", "dhira.peer@akanksha.org", "", "1nwOwQL6eKQoI_RLjWh79kBK778G61c7u", True),
            ("Vocational Labs", "doney.biju@akanksha.org", "", "1I4aJR9MlcZJ6jD90w0bK0B_vuu3ZLt80", True),
            ("Volunteer", "megha.agarwal@akanksha.org", "", "1jKHfN3qtcq2koLjMqcVN2OtoYPjcNWcq", True),
            ("Wadibunder", "prachi.sanghvi@akanksha.org", "Mumbai", "1BiqWixh-PngjP4m76NJb59uscUPxcGeO", True),
        ]

class EmployeeDetails(UserMixin, db.Model):
    __tablename__ = 'employee_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), nullable=True)
    manager = db.Column(db.String(100), nullable=True)  # Manager's email
    manager_name = db.Column(db.String(100), nullable=True)  # Manager's name
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), nullable=True)  # 'Super Admin', 'School Admin', 'Central Admin', 'Pune Staff', 'Mumbai Staff', 'Finance', 'Finance Approver'
    is_active = db.Column(db.Boolean, default=True)

    # Relationship with assigned cities (for Finance personnel)
    city_assignments = db.relationship('CityAssignment', foreign_keys='CityAssignment.employee_id', backref='employee', lazy=True)

    # Flask-Login required methods
    def get_id(self):
        """Return the user ID as a string"""
        return str(self.id)

    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return True

    def is_anonymous(self):
        """Return True if the user is anonymous"""
        return False

    def is_active_user(self):
        """Return True if the user account is active"""
        return self.is_active

    def __repr__(self):
        return f'<EmployeeDetails {self.name} ({self.email})>'

    @staticmethod
    def get_default_employees():
        """Return the default employee data for initialization from CSV file"""
        import csv
        import os

        csv_file_path = os.path.join('uploads', 'Employee Details.csv')

        if not os.path.exists(csv_file_path):
            print(f"WARNING: CSV file not found at {csv_file_path}")
            print("Using minimal default employee data...")
            # Return minimal essential employees if CSV is not available
            return [
                ("nikhil.aher@akanksha.org", "NIKAHE160185", "saurabh.taneja@akanksha.org", "NIKHIL RAJESH AHER", "Super Admin", True),
                ("saurabh.taneja@akanksha.org", "SAUTAN", "", "SAURABH TANEJA", "Super Admin", True),
                ("megha.agarwal@akanksha.org", "MEGAGA", "", "MEGHA AGARWAL", "Super Admin", True),
                ("manoj.balamkar@akanksha.org", "MANBAL", "", "MANOJ BALAMKAR", "Finance Approver", True),
                ("karishma.bhoir@akanksha.org", "KARBHO", "manoj.balamkar@akanksha.org", "KARISHMA BHOIR", "Finance Approver", True),
            ]

        try:
            employee_data = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                for row in csv_reader:
                    # Extract and clean data
                    email = row.get('email', '').strip().lower()
                    employee_id = row.get('employee_id', '').strip()
                    manager = row.get('manager', '').strip().lower()
                    manager_name = row.get('manager_name', '').strip()
                    name = row.get('name', '').strip()
                    role = row.get('role', 'user').strip()
                    is_active = str(row.get('is_active', '1')).lower() in ['true', 'yes', '1', 'active', 'y']

                    # Skip rows without email
                    if not email:
                        continue

                    # Handle empty manager
                    manager_value = manager if manager else ""

                    employee_data.append((email, employee_id, manager_value, name, role, is_active))

            print(f"Loaded {len(employee_data)} employees from CSV file")
            return employee_data

        except Exception as e:
            print(f"ERROR: Failed to read CSV file: {e}")
            print("Using minimal default employee data...")
            # Return minimal essential employees if CSV reading fails
            return [
                ("nikhil.aher@akanksha.org", "NIKAHE160185", "saurabh.taneja@akanksha.org", "NIKHIL RAJESH AHER", "Super Admin", True),
                ("saurabh.taneja@akanksha.org", "SAUTAN", "", "SAURABH TANEJA", "Super Admin", True),
                ("megha.agarwal@akanksha.org", "MEGAGA", "", "MEGHA AGARWAL", "Super Admin", True),
                ("manoj.balamkar@akanksha.org", "MANBAL", "", "MANOJ BALAMKAR", "Finance Approver", True),
                ("karishma.bhoir@akanksha.org", "KARBHO", "manoj.balamkar@akanksha.org", "KARISHMA BHOIR", "Finance Approver", True),
            ]

class CityAssignment(db.Model):
    __tablename__ = 'city_assignment'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_details.id'), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('employee_details.id'), nullable=True)
    assigned_by_employee = db.relationship('EmployeeDetails', foreign_keys=[assigned_by])
    assigned_on = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<CityAssignment {self.employee_id} - {self.city}>'

class SettingsFinance(db.Model):
    __tablename__ = 'settings_finance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setting_name = db.Column(db.String(100), nullable=False, unique=True)
    setting_value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Fields for tracking changes
    updated_by = db.Column(db.String(100), nullable=True)  # Email of the user who last updated
    updated_on = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    previous_value = db.Column(db.String(100), nullable=True)  # Store previous value for logging

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

    @staticmethod
    def get_default_expense_heads():
        """Return the default expense head data for initialization"""
        return [
            ("Staff tea and refreshments", "Staff Welfare", "", True),
            ("Staff annual lunch", "Staff Welfare", "", True),
            ("Staff retreat", "Staff Welfare", "", True),
            ("Staff momentos", "Staff Welfare", "", True),
            ("Education Material", "Education Expenses", "", True),
            ("Art Material", "Education Expenses", "", True),
            ("Teachers' reference books", "Education Expenses", "", True),
            ("Science Lab kits and other equipment", "Education Expenses", "", True),
            ("Students' External Evaluation fees & expenses", "Education Expenses", "", True),
            ("Field Trips", "Education Expenses", "", True),
            ("Educational Software Subscriptions", "Education Expenses", "", True),
            ("SDR Expenses", "Education Expenses", "", True),
            ("Exam Fees", "Education Expenses", "", True),
            ("Annual day", "School Events", "", True),
            ("Fairs and Festival Celebrations", "School Events", "", True),
            ("SSC farewell", "School Events", "", True),
            ("Sports Day - Food/Fees", "Sports Expenses", "", True),
            ("Sports Day - Venue", "Sports Expenses", "", True),
            ("Sports Material and Equipment", "Sports Expenses", "", True),
            ("Akanksha Sports event", "Sports Expenses", "", True),
            ("External Sports event", "Sports Expenses", "", True),
            ("Mid-Day Meal Contingency", "603000 - Child Welfare", "", True),
            ("Medical Welfare Expenses", "603001 - Child Welfare", "", True),
            ("School clubs", "603002 - Child Welfare", "", True),
            ("External Visit", "Community Engagement", "", True),
            ("Local Events", "Community Engagement", "", True),
            ("Local Conveyance", "Travel Expenses", "", True),
            ("Domestic Travel", "Travel Expenses", "", True),
            ("International travel", "Travel Expenses", "", True),
            ("Postage & Courier", "Communication", "", True),
            ("Telephone & Internet", "Communication", "", True),
            ("Stationery, photocopying, printing & computer accessories", "Printing & Stationery", "", True),
            ("Rent", "Rent, Electricity And Other Utilities", "", True),
            ("Electricity", "Rent, Electricity And Other Utilities", "", True),
            ("Utility & Water Charges", "Rent, Electricity And Other Utilities", "", True),
            ("Repair costs", "Repairs & Maintenance", "", True),
            ("Maintenance expenses", "Repairs & Maintenance", "", True),
            ("AMC", "Repairs & Maintenance", "", True),
            ("Cleaning & cleaning Supplies", "Repairs & Maintenance", "", True),
            ("Video Creation Expenses", "Communication/Fund Raising Expenses", "", True),
            ("Events", "Communication/Fund Raising Expenses", "", True),
            ("Billdesk Charges", "Communication/Fund Raising Expenses", "", True),
            ("Other Communication Expense", "Communication/Fund Raising Expenses", "", True),
            ("Website Maintenance", "Communication/Fund Raising Expenses", "", True),
            ("Bank Charges", "Other Expenses", "", True),
            ("Other Administrative Expenses", "Other Expenses", "", True),
            ("D & O Insurance", "Other Expenses", "", True),
            ("E & O Policy", "Other Expenses", "", True),
            ("Broadform Liability (CGL)", "Other Expenses", "", True),
            ("Membership & Subscriptions", "Other Expenses", "", True),
            ("Legal Fees", "Legal and Professional Charges", "", True),
            ("Other Legal Expenses", "Legal and Professional Charges", "", True),
            ("Professional Fees", "Legal and Professional Charges", "", True),
            ("Audit Fees", "Legal and Professional Charges", "", True),
            ("Training Events - Edventure", "Training & Capacity Building expenses", "", True),
            ("Other Training Events - Internal", "Training & Capacity Building expenses", "", True),
            ("Other Training Events - External", "Training & Capacity Building expenses", "", True),
            ("Resource person fee", "Training & Capacity Building expenses", "", True),
        ]

class EPV(db.Model):
    """
    Model to store all expense voucher data
    """
    __tablename__ = 'epv'
    __table_args__ = (
        db.CheckConstraint('from_date <= to_date', name='check_date_range'),
        db.CheckConstraint('total_amount >= 0', name='check_positive_amount'),
    )

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.String(60), unique=True, nullable=False)  # EPV-YYYYMMDD-CostCenterName-HASH format

    # Employee details
    email_id = db.Column(db.String(100), nullable=False, index=True)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False, index=True)

    # Date range
    from_date = db.Column(db.Date, nullable=False, index=True)
    to_date = db.Column(db.Date, nullable=False, index=True)

    # Payment and acknowledgement
    payment_to = db.Column(db.String(100), nullable=False)  # Previously expense_type
    acknowledgement = db.Column(db.String(255))  # For any acknowledgement information

    # Document status for supplementary documents
    document_status = db.Column(db.String(50), default='complete')  # 'complete', 'pending_additional_documents'
    requested_documents = db.Column(db.Text, nullable=True)  # JSON string describing what's missing

    # Metadata
    submission_date = db.Column(db.DateTime, default=datetime.now)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"

    # Cost center
    cost_center_id = db.Column(db.Integer, db.ForeignKey('costcenter.id'))
    cost_center = db.relationship('CostCenter', backref=db.backref('expenses', lazy=True))
    cost_center_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=True)  # City for the expense (may differ from cost center's city)

    # File storage details
    file_url = db.Column(db.String(255))  # URL to access the file in Google Drive
    drive_file_id = db.Column(db.String(100))  # Google Drive file ID

    # Financial details
    total_amount = db.Column(db.Float, nullable=False)
    amount_in_words = db.Column(db.String(255))

    # Split invoice support
    invoice_type = db.Column(db.String(20), default='standard')  # standard, master, sub, split
    master_invoice_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=True)  # For sub-invoices, points to master
    master_invoice = db.relationship('EPV', foreign_keys=[master_invoice_id], backref=db.backref('sub_invoices', lazy='joined'), remote_side='EPV.id')
    split_status = db.Column(db.String(20), nullable=True)  # splitting, pending_approval, partially_approved, fully_approved, rejected, processing, completed

    # New split invoice fields for single EPV with multiple approvers
    approved_amount = db.Column(db.Float, default=0.0)  # Total amount approved from allocations
    rejected_amount = db.Column(db.Float, default=0.0)  # Total amount rejected from allocations
    pending_amount = db.Column(db.Float, default=0.0)   # Total amount still pending approval

    # Approval workflow
    status = db.Column(db.String(20), default='submitted', index=True)  # submitted, pending_approval, approved, rejected, partially_approved, finance_pending, finance_processed, finance_approved, finance_rejected
    # The overall status is determined by the individual approver statuses in EPVApproval
    # If all approvers approve, status = 'approved'
    # If any approver rejects, status = 'rejected'
    # If some approve and none reject, status = 'partially_approved'

    # Finance processing fields
    finance_status = db.Column(db.String(20), nullable=True)  # pending, processed, approved, rejected

    # Fields to track who is currently processing this EPV
    being_processed_by = db.Column(db.Integer, db.ForeignKey('employee_details.id'), nullable=True)
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processor = db.relationship('EmployeeDetails', foreign_keys=[being_processed_by])

    # Legacy fields (kept for backward compatibility)
    approver_emails = db.Column(db.Text)  # Comma-separated list of approver emails
    approved_by = db.Column(db.String(100))  # Email of the approver
    approved_on = db.Column(db.DateTime)  # When it was approved
    rejected_by = db.Column(db.String(100))  # Email of the person who rejected
    rejected_on = db.Column(db.DateTime)  # When it was rejected
    rejection_reason = db.Column(db.Text)  # Why it was rejected

    def __repr__(self):
        return f"<EPV {self.epv_id}>"

class FinanceEntry(db.Model):
    __tablename__ = 'finance_entry'
    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('finance_entry', uselist=False, lazy=True))

    # Who processed this entry
    finance_user_id = db.Column(db.Integer, db.ForeignKey('employee_details.id'), nullable=False)
    finance_user = db.relationship('EmployeeDetails', foreign_keys=[finance_user_id])

    # Entry details
    entry_date = db.Column(db.DateTime, default=datetime.now)
    vendor_name = db.Column(db.String(100), nullable=False)
    journal_entry = db.Column(db.String(50), nullable=False)
    payment_voucher = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    fcra_status = db.Column(db.String(20), nullable=False)  # 'FCRA', 'Non-FCRA'
    comments = db.Column(db.Text, nullable=True)

    # Partial payment support
    is_partial_payment = db.Column(db.Boolean, default=False)

    # Payment 1 fields
    journal_entry_1 = db.Column(db.String(50), nullable=True)  # Journal entry for first payment
    payment_voucher_1 = db.Column(db.String(50), nullable=True)  # Payment voucher for first payment
    amount_1 = db.Column(db.Float, nullable=True)  # First partial amount
    fcra_status_1 = db.Column(db.String(20), nullable=True)  # FCRA status for first amount
    transaction_id_1 = db.Column(db.String(100), nullable=True)  # Transaction ID for first payment
    payment_date_1 = db.Column(db.DateTime, nullable=True)  # Payment date for first payment

    # Payment 2 fields
    journal_entry_2 = db.Column(db.String(50), nullable=True)  # Journal entry for second payment
    payment_voucher_2 = db.Column(db.String(50), nullable=True)  # Payment voucher for second payment
    amount_2 = db.Column(db.Float, nullable=True)  # Second partial amount
    fcra_status_2 = db.Column(db.String(20), nullable=True)  # FCRA status for second amount
    transaction_id_2 = db.Column(db.String(100), nullable=True)  # Transaction ID for second payment
    payment_date_2 = db.Column(db.DateTime, nullable=True)  # Payment date for second payment

    # Payment details (added fields)
    transaction_id = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)

    # Approval details
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approver_id = db.Column(db.Integer, db.ForeignKey('employee_details.id'), nullable=True)
    approver = db.relationship('EmployeeDetails', foreign_keys=[approver_id])
    approved_on = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FinanceEntry {self.id} for EPV {self.epv_id}>'

class EPVApproval(db.Model):
    """
    Model to store approval status for each approver of an EPV
    """
    __tablename__ = 'epv_approval'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('approvals', lazy=True))

    # Link to allocation for split invoices (nullable for backward compatibility)
    allocation_id = db.Column(db.Integer, db.ForeignKey('epv_allocation.id'), nullable=True)
    allocation = db.relationship('EPVAllocation', backref=db.backref('approval', uselist=False))

    # Approver details
    approver_email = db.Column(db.String(100), nullable=False, index=True)
    approver_name = db.Column(db.String(100))

    # Approval status
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, rejected
    action_date = db.Column(db.DateTime)  # When the approver took action
    comments = db.Column(db.Text)  # Any comments from the approver

    # Token for secure approval/rejection links
    token = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f"<EPVApproval {self.id} for EPV {self.epv_id} by {self.approver_email}>"

class EPVAllocation(db.Model):
    """
    Model to store cost center allocations for split invoices
    Each allocation represents a portion of the total invoice amount allocated to a specific cost center with a designated approver
    """
    __tablename__ = 'epv_allocation'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('allocations', lazy=True))

    # Cost center details
    cost_center_id = db.Column(db.Integer, db.ForeignKey('costcenter.id'), nullable=False)
    cost_center_name = db.Column(db.String(100), nullable=False)
    cost_center = db.relationship('CostCenter', foreign_keys=[cost_center_id])

    # Allocation details
    allocated_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    expense_head = db.Column(db.String(100), nullable=True)  # Expense head for this allocation

    # Approver details
    approver_email = db.Column(db.String(100), nullable=False)
    approver_name = db.Column(db.String(100), nullable=True)

    # Approval status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    action_date = db.Column(db.DateTime, nullable=True)  # When the approver took action
    rejection_reason = db.Column(db.Text, nullable=True)  # Reason for rejection if rejected

    # Token for secure approval/rejection links
    token = db.Column(db.String(100), unique=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<EPVAllocation {self.id} for EPV {self.epv_id} - {self.cost_center_name} - Rs. {self.allocated_amount}>"

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

    # Split invoice flag
    split_invoice = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<EPVItem {self.id} for EPV {self.epv_id}>"



class SupplementaryDocument(db.Model):
    """
    Model to store supplementary documents for EPVs
    """
    __tablename__ = 'supplementary_document'

    id = db.Column(db.Integer, primary_key=True)
    epv_id = db.Column(db.Integer, db.ForeignKey('epv.id'), nullable=False)
    epv = db.relationship('EPV', backref=db.backref('supplementary_documents', lazy=True))

    # Document details
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    drive_file_id = db.Column(db.String(100), nullable=True)

    # Metadata
    uploaded_by = db.Column(db.String(100), nullable=False)  # Email of the uploader
    uploaded_on = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.Text, nullable=True)  # Description of the document

    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected

    def __repr__(self):
        return f"<SupplementaryDocument {self.id} for EPV {self.epv_id}>"

# User and OAuth models removed - using EmployeeDetails for Flask-Login instead

# Sync function removed - no longer needed since we use EmployeeDetails directly for authentication

def init_db(app):
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()

        print("Database initialized with all tables.")

        inspector = inspect(db.engine)

        # Initialize cost centers if the table is empty
        if not inspector.has_table('costcenter') or CostCenter.query.count() == 0:
            print("Initializing cost centers with comprehensive data...")

            # Get the default cost center data
            cost_center_data = CostCenter.get_default_cost_centers()

            # Add each cost center to the database
            for costcenter, approver_email, city, drive_id, is_active in cost_center_data:
                # Handle empty city values
                city_value = city if city.strip() else None

                cost_center = CostCenter(
                    costcenter=costcenter,
                    approver_email=approver_email,
                    city=city_value,
                    drive_id=drive_id,
                    is_active=is_active
                )
                db.session.add(cost_center)

            # Commit the changes
            db.session.commit()
            print(f"Database initialized with {len(cost_center_data)} cost centers.")

        # Initialize employee details if the table is empty
        print("DEBUG: Checking employee_details table...")
        if not inspector.has_table('employee_details'):
            print("DEBUG: employee_details table does not exist, creating it...")
        elif EmployeeDetails.query.count() == 0:
            print("DEBUG: employee_details table exists but is empty, populating it...")
        else:
            print(f"DEBUG: employee_details table exists and has {EmployeeDetails.query.count()} records.")

        if not inspector.has_table('employee_details') or EmployeeDetails.query.count() == 0:
            print("Initializing employee details from CSV data...")

            # Get the default employee data (loads from CSV if available)
            employee_data = EmployeeDetails.get_default_employees()

            # Add each employee to the database
            for email, employee_id, manager, name, role, is_active in employee_data:
                # Handle empty manager values
                manager_value = manager.lower() if manager.strip() else None

                employee = EmployeeDetails(
                    email=email.lower(),
                    employee_id=employee_id,
                    manager=manager_value,
                    name=name,
                    role=role,
                    is_active=is_active
                )
                db.session.add(employee)

            # Commit the changes
            db.session.commit()
            print(f"Database initialized with {len(employee_data)} employees.")

        # User sync no longer needed - using EmployeeDetails directly for authentication

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
                    "description": "Maximum number of days in the past for expense claims"
                },
                {
                    "setting_name": "max_days_processing",
                    "setting_value": "5",
                    "description": "Maximum number of days for processing expenses (SOP)"
                },
                {
                    "setting_name": "max_reminder_days",
                    "setting_value": "2",
                    "description": "Number of days after which a reminder is sent to manager if approval is pending"
                }
            ]

            # Add settings to the database
            for setting_data in settings:
                setting = SettingsFinance(
                    setting_name=setting_data["setting_name"],
                    setting_value=setting_data["setting_value"],
                    description=setting_data["description"]
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
            print("Initializing expense heads with comprehensive data...")

            # Get the default expense head data
            expense_head_data = ExpenseHead.get_default_expense_heads()

            # Add each expense head to the database
            for head_name, head_code, description, is_active in expense_head_data:
                # Handle empty description values
                description_value = description if description.strip() else None

                expense_head = ExpenseHead(
                    head_name=head_name,
                    head_code=head_code,
                    description=description_value,
                    is_active=is_active
                )
                db.session.add(expense_head)

            # Commit the changes
            db.session.commit()
            print(f"Database initialized with {len(expense_head_data)} expense heads.")

        # Update epv_id column size if needed
        if inspector.has_table('epv'):
            columns = [col for col in inspector.get_columns('epv')]
            epv_id_column = next((col for col in columns if col['name'] == 'epv_id'), None)

            if epv_id_column:
                # Check if the column size needs to be updated
                current_length = epv_id_column.get('type').length if hasattr(epv_id_column.get('type'), 'length') else None
                if current_length and current_length < 60:
                    print(f"Updating epv_id column size from {current_length} to 60 characters")
                    with db.engine.connect() as conn:
                        conn.execute(db.text('ALTER TABLE epv MODIFY COLUMN epv_id VARCHAR(60) NOT NULL'))
                        conn.commit()
                    print("epv_id column size updated successfully")
                else:
                    print("epv_id column size is already adequate")
            else:
                print("epv_id column not found in epv table")
        else:
            print("epv table does not exist yet")

        # Add partial payment columns to finance_entry table if they don't exist
        if inspector.has_table('finance_entry'):
            columns = [col['name'] for col in inspector.get_columns('finance_entry')]

            if 'is_partial_payment' not in columns:
                print("Adding is_partial_payment column to finance_entry table")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE finance_entry ADD COLUMN is_partial_payment BOOLEAN DEFAULT FALSE'))
                    conn.commit()
            else:
                print("is_partial_payment column already exists in finance_entry table")

            if 'amount_1' not in columns:
                print("Adding amount_1 column to finance_entry table")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE finance_entry ADD COLUMN amount_1 FLOAT'))
                    conn.commit()
            else:
                print("amount_1 column already exists in finance_entry table")

            if 'fcra_status_1' not in columns:
                print("Adding fcra_status_1 column to finance_entry table")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE finance_entry ADD COLUMN fcra_status_1 VARCHAR(20)'))
                    conn.commit()
            else:
                print("fcra_status_1 column already exists in finance_entry table")

            if 'amount_2' not in columns:
                print("Adding amount_2 column to finance_entry table")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE finance_entry ADD COLUMN amount_2 FLOAT'))
                    conn.commit()
            else:
                print("amount_2 column already exists in finance_entry table")

            if 'fcra_status_2' not in columns:
                print("Adding fcra_status_2 column to finance_entry table")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE finance_entry ADD COLUMN fcra_status_2 VARCHAR(20)'))
                    conn.commit()
            else:
                print("fcra_status_2 column already exists in finance_entry table")

            # Add additional partial payment fields
            additional_fields = [
                ('journal_entry_1', 'VARCHAR(50)', 'Journal Entry 1'),
                ('payment_voucher_1', 'VARCHAR(50)', 'Payment Voucher 1'),
                ('transaction_id_1', 'VARCHAR(100)', 'Transaction ID 1'),
                ('payment_date_1', 'DATETIME', 'Payment Date 1'),
                ('journal_entry_2', 'VARCHAR(50)', 'Journal Entry 2'),
                ('payment_voucher_2', 'VARCHAR(50)', 'Payment Voucher 2'),
                ('transaction_id_2', 'VARCHAR(100)', 'Transaction ID 2'),
                ('payment_date_2', 'DATETIME', 'Payment Date 2')
            ]

            for field_name, field_type, _ in additional_fields:
                if field_name not in columns:
                    print(f"Adding {field_name} column to finance_entry table")
                    with db.engine.connect() as conn:
                        conn.execute(db.text(f'ALTER TABLE finance_entry ADD COLUMN {field_name} {field_type}'))
                        conn.commit()
                else:
                    print(f"{field_name} column already exists in finance_entry table")
