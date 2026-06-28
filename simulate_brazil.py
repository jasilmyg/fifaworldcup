from app import create_app
from models import db, Match, Prediction, User
from utils.point_calculator import calculate_prediction_points

app = create_app()

with app.app_context():
    match = Match.query.filter_by(home_team='Brazil', away_team='Japan').first()
    if match:
        match.home_score = 3
        match.away_score = 2
        match.status = 'completed'
        db.session.commit()
        
        predictions = Prediction.query.filter_by(match_id=match.id, status='pending').all()
        for pred in predictions:
            points = calculate_prediction_points(pred, match)
            pred.points_awarded = points
            pred.status = 'scored'
            
            user = User.query.get(pred.user_id)
            if user:
                user.points += points
                
        db.session.commit()
        print("Brazil match simulated as 3-2!")
    else:
        print("Match not found.")
