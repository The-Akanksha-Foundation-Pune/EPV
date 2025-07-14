import os
from flask import Flask
from models import db
import urllib.parse
from sqlalchemy import text

# Optional: load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Use the same DB URI logic as run_init_db.py
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')

if DB_HOST and DB_USER and DB_PASSWORD and DB_NAME:
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT or 3306}/{DB_NAME}"
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///epv.db'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'temp-secret-for-init'

db.init_app(app)  # Register the app with SQLAlchemy

def reinit_db():
    with app.app_context():
        print('⚠️  Disabling foreign key checks (if MySQL)...')
        try:
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        except Exception:
            pass  # Ignore if not MySQL
        print('⚠️  Dropping all tables...')
        db.drop_all()
        print('✅ All tables dropped.')
        try:
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        except Exception:
            pass
        print('🗄️  Creating all tables from models...')
        db.create_all()
        print('✅ All tables created.')
        print('🎉 Database reinitialized successfully!')

if __name__ == '__main__':
    reinit_db() 