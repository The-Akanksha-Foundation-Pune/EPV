from models import db, SettingsFinance
from app import app

CAR_ALLOWANCE_DEFAULT = 12.0  # Change as needed
BIKE_ALLOWANCE_DEFAULT = 6.0  # Change as needed

with app.app_context():
    car_setting = SettingsFinance.query.filter_by(setting_name='car_allowance').first()
    bike_setting = SettingsFinance.query.filter_by(setting_name='bike_allowance').first()
    added = False
    if not car_setting:
        db.session.add(SettingsFinance(setting_name='car_allowance', setting_value=str(CAR_ALLOWANCE_DEFAULT)))
        print(f"Added car_allowance = {CAR_ALLOWANCE_DEFAULT}")
        added = True
    else:
        print(f"car_allowance already exists with value: {car_setting.setting_value}")
    if not bike_setting:
        db.session.add(SettingsFinance(setting_name='bike_allowance', setting_value=str(BIKE_ALLOWANCE_DEFAULT)))
        print(f"Added bike_allowance = {BIKE_ALLOWANCE_DEFAULT}")
        added = True
    else:
        print(f"bike_allowance already exists with value: {bike_setting.setting_value}")
    if added:
        db.session.commit()
        print("Settings committed to database.")
    else:
        print("No changes made.") 