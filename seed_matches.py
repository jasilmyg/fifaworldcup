from app import create_app
from models import db, Match
from datetime import datetime

app = create_app()

matches = [
    {
        "home_team": "Brazil",
        "away_team": "Germany",
        "kickoff_time": datetime(2026, 6, 29, 18, 0),
        "venue": "Estadio Azteca"
    },
    {
        "home_team": "Argentina",
        "away_team": "France",
        "kickoff_time": datetime(2026, 6, 30, 20, 0),
        "venue": "MetLife Stadium"
    },
    {
        "home_team": "Spain",
        "away_team": "Portugal",
        "kickoff_time": datetime(2026, 7, 1, 18, 0),
        "venue": "Lumen Field"
    },
    {
        "home_team": "England",
        "away_team": "Italy",
        "kickoff_time": datetime(2026, 7, 2, 20, 0),
        "venue": "Levi's Stadium"
    },
    {
        "home_team": "Netherlands",
        "away_team": "Senegal",
        "kickoff_time": datetime(2026, 7, 3, 16, 0),
        "venue": "NRG Stadium"
    }
]

with app.app_context():
    for match_data in matches:
        match = Match(
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            kickoff_time=match_data["kickoff_time"],
            venue=match_data["venue"]
        )
        db.session.add(match)
        print(f"Added match: {match.home_team} vs {match.away_team}")
        
    db.session.commit()
    print("Successfully added all matches!")
