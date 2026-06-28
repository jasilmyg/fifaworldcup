from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    referral_code = db.Column(db.String(20), unique=True, nullable=True)
    referred_by = db.Column(db.String(20), nullable=True)
    points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(500), default="") # Comma-separated badges
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_logo = db.Column(db.String(255), nullable=True)
    away_logo = db.Column(db.String(255), nullable=True)
    kickoff_time = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=True)
    
    # Status: upcoming, completed, pending_result
    status = db.Column(db.String(20), default='upcoming')
    
    # Results
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    
    predictions = db.relationship('Prediction', backref='match', lazy=True)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    
    # winner prediction: home, away, draw
    winner = db.Column(db.String(20), nullable=False)
    
    # exact score prediction
    home_score = db.Column(db.Integer, nullable=False)
    away_score = db.Column(db.Integer, nullable=False)
    
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_awarded = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending') # pending, scored
    
    # Ensure one prediction per user per match
    __table_args__ = (db.UniqueConstraint('user_id', 'match_id', name='_user_match_uc'),)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
