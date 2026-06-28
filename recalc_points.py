from app import create_app
from models import db, Prediction, User, Match
from utils.point_calculator import calculate_prediction_points

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        user.points = 0
        user.current_streak = 0
        
    predictions = Prediction.query.filter_by(status='scored').order_by(Prediction.predicted_at).all()
    for pred in predictions:
        match = Match.query.get(pred.match_id)
        points = calculate_prediction_points(pred, match)
        pred.points_awarded = points
        
        user = User.query.get(pred.user_id)
        if user:
            user.points += points
            if points > 0:
                user.current_streak += 1
            else:
                user.current_streak = 0
            
    db.session.commit()
    print("All points and streaks recalculated!")
