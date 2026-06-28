from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Match, Prediction, User, Log
from utils.point_calculator import calculate_prediction_points
from utils.google_sheet import GoogleSheetSync
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_matches = Match.query.count()
    pending_matches = Match.query.filter(Match.kickoff_time > datetime.utcnow()).count()
    completed_matches = Match.query.filter_by(status='completed').count()
    matches = Match.query.order_by(Match.kickoff_time.desc()).all()
    
    return render_template('admin/dashboard.html', total_users=total_users, total_matches=total_matches, pending_matches=pending_matches, completed_matches=completed_matches, matches=matches)

@admin_bp.route('/add_match', methods=['POST'])
@login_required
@admin_required
def add_match():
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    kickoff_time_str = request.form.get('kickoff_time')
    
    if kickoff_time_str:
        kickoff_time = datetime.strptime(kickoff_time_str, '%Y-%m-%dT%H:%M')
    else:
        flash('Kickoff time is required.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    venue = request.form.get('venue')
    
    match = Match(home_team=home_team, away_team=away_team, kickoff_time=kickoff_time, venue=venue)
    db.session.add(match)
    db.session.commit()
    
    GoogleSheetSync.sync_match(match)
    GoogleSheetSync.log_action(f"Added match {home_team} vs {away_team}")
    
    flash('Match added successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/enter_score/<int:match_id>', methods=['POST'])
@login_required
@admin_required
def enter_score(match_id):
    match = Match.query.get_or_404(match_id)
    home_score = int(request.form.get('home_score', 0))
    away_score = int(request.form.get('away_score', 0))
    
    match.home_score = home_score
    match.away_score = away_score
    match.status = 'completed'
    db.session.commit()
    
    predictions = Prediction.query.filter_by(match_id=match_id, status='pending').all()
    for pred in predictions:
        points = calculate_prediction_points(pred, match)
        pred.points_awarded = points
        pred.status = 'scored'
        
        user = User.query.get(pred.user_id)
        if user:
            user.points += points
            if points > 0:
                user.current_streak += 1
            else:
                user.current_streak = 0
        
    db.session.commit()
    
    GoogleSheetSync.sync_result(match)
    GoogleSheetSync.log_action(f"Entered score for match {match_id}: {home_score}-{away_score}")
    
    flash('Score entered and points updated.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/force_sync', methods=['POST'])
@login_required
@admin_required
def force_sync():
    result_msg = GoogleSheetSync.sync_down()
    flash(result_msg, 'success')
    return redirect(url_for('admin.dashboard'))
