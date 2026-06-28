from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Match, Prediction
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile')
@login_required
def profile():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.predicted_at.desc()).all()
    total_scored = sum(1 for p in predictions if p.status == 'scored')
    correct_predictions = sum(1 for p in predictions if p.points_awarded > 0)
    accuracy = (correct_predictions / total_scored * 100) if total_scored > 0 else 0
    
    return render_template('profile.html', predictions=predictions, accuracy=accuracy, total_scored=total_scored, correct_predictions=correct_predictions)

@user_bp.route('/predict/<int:match_id>', methods=['POST'])
@login_required
def predict(match_id):
    match = Match.query.get_or_404(match_id)
    
    if datetime.utcnow() >= match.kickoff_time - timedelta(minutes=30):
        flash('Prediction closed for this match.', 'danger')
        return redirect(url_for('main.index'))
        
    winner = request.form.get('winner')
    home_score = int(request.form.get('home_score', 0))
    away_score = int(request.form.get('away_score', 0))
    
    prediction = Prediction.query.filter_by(user_id=current_user.id, match_id=match_id).first()
    
    if prediction:
        prediction.winner = winner
        prediction.home_score = home_score
        prediction.away_score = away_score
        prediction.predicted_at = datetime.utcnow()
        flash('Prediction updated successfully.', 'success')
    else:
        prediction = Prediction(user_id=current_user.id, match_id=match_id, winner=winner, home_score=home_score, away_score=away_score)
        db.session.add(prediction)
        flash('Prediction submitted successfully.', 'success')
        
    db.session.commit()
    
    try:
        from utils.google_sheet import GoogleSheetSync
        GoogleSheetSync.sync_prediction(prediction)
        GoogleSheetSync.log_action(f"User {current_user.name} predicted match {match_id}")
    except Exception as e:
        print(f"Error syncing prediction: {e}")
        
    return redirect(url_for('main.index'))
