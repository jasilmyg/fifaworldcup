import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-fifa-key'
    if os.environ.get('VERCEL') == '1':
        default_db = 'sqlite:////tmp/app.db'
    else:
        default_db = 'sqlite:///' + os.path.join(basedir, 'database', 'app.db')
        
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optional: Configure other variables here if needed
