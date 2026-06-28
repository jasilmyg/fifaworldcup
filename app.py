import os
from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from routes.auth import auth_bp, bcrypt
from routes.main import main_bp
from routes.user import user_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Ensure database directory exists
    os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)
    
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(mobile='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(name='Admin', mobile='admin', password=hashed_pw, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: mobile=admin, password=admin123")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
