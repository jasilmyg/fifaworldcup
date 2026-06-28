from flask import Blueprint, render_template
from flask_login import current_user
from models import Match, User
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        predicted_ids = [p.match_id for p in current_user.predictions]
        if predicted_ids:
            upcoming_matches = Match.query.filter(
                Match.kickoff_time > datetime.utcnow(),
                Match.id.notin_(predicted_ids)
            ).order_by(Match.kickoff_time.asc()).limit(5).all()
        else:
            upcoming_matches = Match.query.filter(Match.kickoff_time > datetime.utcnow()).order_by(Match.kickoff_time.asc()).limit(5).all()
    else:
        upcoming_matches = Match.query.filter(Match.kickoff_time > datetime.utcnow()).order_by(Match.kickoff_time.asc()).limit(5).all()
        
    completed_matches = Match.query.filter_by(status='completed').order_by(Match.kickoff_time.desc()).limit(5).all()
    total_participants = User.query.count()
    return render_template('index.html', upcoming_matches=upcoming_matches, completed_matches=completed_matches, total_participants=total_participants)

@main_bp.route('/rules')
def rules():
    return render_template('rules.html')

@main_bp.route('/leaderboard')
def leaderboard():
    top_users = User.query.filter_by(is_admin=False).order_by(User.points.desc()).all()
    return render_template('leaderboard.html', users=top_users)
