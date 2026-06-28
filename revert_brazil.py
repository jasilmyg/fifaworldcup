from app import create_app
from models import db, Match, Prediction, User

app = create_app()

with app.app_context():
    match = Match.query.filter_by(home_team='Brazil', away_team='Japan').first()
    if match:
        match.home_score = 0
        match.away_score = 0
        match.status = 'pending'
        
        predictions = Prediction.query.filter_by(match_id=match.id).all()
        for pred in predictions:
            user = User.query.get(pred.user_id)
            if user:
                user.points -= pred.points_awarded
                
            pred.points_awarded = 0
            pred.status = 'pending'
            
        db.session.commit()
        print("Brazil match and all associated points reverted to pending!")
    else:
        print("Match not found.")
