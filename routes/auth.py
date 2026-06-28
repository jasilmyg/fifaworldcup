from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        user = User.query.filter_by(mobile=mobile).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check mobile number and password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        district = request.form.get('district')
        state = request.form.get('state')
        password = request.form.get('password')
        referral = request.form.get('referral')
        
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        import random
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, mobile=mobile, email=email, district=district, state=state, password=hashed_pw, referred_by=referral)
        user.referral_code = (mobile[-4:] + name[:2]).upper() if name and mobile else 'REF'
        
        while True:
            new_id = random.randint(10000, 99999)
            if not User.query.get(new_id):
                user.id = new_id
                break
        
        db.session.add(user)
        db.session.commit()
        
        # Referral bonus logic
        if referral:
            referrer = User.query.filter_by(referral_code=referral).first()
            if referrer:
                referrer.points += 15
                user.points += 15 # Bonus for signing up with referral
                db.session.commit()
                
        try:
            from utils.google_sheet import GoogleSheetSync
            GoogleSheetSync.sync_user(user)
            GoogleSheetSync.log_action(f"New user registered: {user.name}")
        except Exception as e:
            print(f"Error syncing user: {e}")
            
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
