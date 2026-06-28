from app import create_app
from models import db, Match, Prediction
from datetime import datetime

app = create_app()

matches = [
    {
        "home_team": "Brazil",
        "away_team": "Japan",
        "kickoff_time": datetime(2026, 6, 29, 17, 0), # 17:00 GMT
        "venue": "Houston Stadium"
    },
    {
        "home_team": "Germany",
        "away_team": "Paraguay",
        "kickoff_time": datetime(2026, 6, 29, 20, 30), # 20:30 GMT
        "venue": "Boston Stadium"
    },
    {
        "home_team": "Netherlands",
        "away_team": "Morocco",
        "kickoff_time": datetime(2026, 6, 29, 23, 0), 
        "venue": "Estadio Monterrey"
    },
    {
        "home_team": "Ivory Coast",
        "away_team": "Norway",
        "kickoff_time": datetime(2026, 6, 30, 18, 0),
        "venue": "Miami Stadium"
    }
]

with app.app_context():
    # Clear existing data safely
    Prediction.query.delete()
    Match.query.delete()
    db.session.commit()
    print("Cleared all previous incorrect matches and predictions.")

    # Insert actual matches
    for match_data in matches:
        match = Match(
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            kickoff_time=match_data["kickoff_time"],
            venue=match_data["venue"]
        )
        db.session.add(match)
        print(f"Added REAL match: {match.home_team} vs {match.away_team}")
        
    db.session.commit()
    print("Successfully added the correct real matches!")
