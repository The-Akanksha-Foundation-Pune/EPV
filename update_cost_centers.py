#!/usr/bin/env python3
"""
Script to update CostCenter table with comprehensive cost center data
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, CostCenter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app for database context
app = Flask(__name__)

# Database configuration
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT', '3306')
db_name = os.environ.get('DB_NAME')

# URL encode the password to handle special characters
import urllib.parse
encoded_password = urllib.parse.quote_plus(db_password) if db_password else ''

# Construct the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Cost center data
COST_CENTER_DATA = [
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

def update_cost_centers():
    """Add new cost center data to the CostCenter table"""

    with app.app_context():
        try:
            print("Starting cost center data insertion...")

            # Insert new cost center data
            print("Inserting new cost center data...")
            inserted_count = 0
            
            for costcenter, approver_email, city, drive_id, is_active in COST_CENTER_DATA:
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
                inserted_count += 1
                print(f"Added: {costcenter}")
            
            # Commit all changes
            db.session.commit()
            print(f"\nSuccessfully inserted {inserted_count} cost center records")
            print("Cost center data insertion completed successfully!")
            
        except Exception as e:
            print(f"Error updating cost center data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    update_cost_centers()
