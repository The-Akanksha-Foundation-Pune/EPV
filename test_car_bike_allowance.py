from app import app
from models import db, SettingsFinance

with app.app_context():
    car_setting = SettingsFinance.query.filter_by(setting_name='car_allowance').first()
    bike_setting = SettingsFinance.query.filter_by(setting_name='bike_allowance').first()
    car_allowance = float(car_setting.setting_value) if car_setting else None
    bike_allowance = float(bike_setting.setting_value) if bike_setting else None
    print(f"car_allowance from DB: {car_allowance}")
    print(f"bike_allowance from DB: {bike_allowance}") 