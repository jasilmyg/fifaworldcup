from app import create_app
from models import db, Match
from datetime import datetime, timedelta

app = create_app()

# Realistic Round of 32 fixtures for the 2026 FIFA World Cup
matches = [
    {
        "home_team": "USA",
        "away_team": "Colombia",
        "kickoff_time": datetime(2026, 6, 29, 13, 0),
        "venue": "SoFi Stadium, Los Angeles"
    },
    {
        "home_team": "Portugal",
        "away_team": "Ecuador",
        "kickoff_time": datetime(2026, 6, 29, 17, 0),
        "venue": "AT&T Stadium, Dallas"
    },
    {
        "home_team": "France",
        "away_team": "Morocco",
        "kickoff_time": datetime(2026, 6, 29, 20, 0),
        "venue": "MetLife Stadium, New York"
    },
    {
        "home_team": "England",
        "away_team": "Uruguay",
        "kickoff_time": datetime(2026, 6, 30, 13, 0),
        "venue": "Mercedes-Benz Stadium, Atlanta"
    },
    {
        "home_team": "Brazil",
        "away_team": "South Korea",
        "kickoff_time": datetime(2026, 6, 30, 17, 0),
        "venue": "NRG Stadium, Houston"
    },
    {
        "home_team": "Argentina",
        "away_team": "Switzerland",
        "kickoff_time": datetime(2026, 6, 30, 20, 0),
        "venue": "Hard Rock Stadium, Miami"
    },
    {
        "home_team": "Spain",
        "away_team": "Mexico",
        "kickoff_time": datetime(2026, 7, 1, 15, 0),
        "venue": "Estadio Azteca, Mexico City"
    },
    {
        "home_team": "Germany",
        "away_team": "Japan",
        "kickoff_time": datetime(2026, 7, 1, 19, 0),
        "venue": "BC Place, Vancouver"
    }
]

with app.app_context():
    for match_data in matches:
        # Check if match already exists to avoid duplicates
        existing = Match.query.filter_by(
            home_team=match_data["home_team"], 
            away_team=match_data["away_team"]
        ).first()
        
        if not existing:
            match = Match(
                home_team=match_data["home_team"],
                away_team=match_data["away_team"],
                kickoff_time=match_data["kickoff_time"],
                venue=match_data["venue"]
            )
            db.session.add(match)
            print(f"Added realistic match: {match.home_team} vs {match.away_team}")
        else:
            print(f"Match already exists: {match_data['home_team']} vs {match_data['away_team']}")
            
    db.session.commit()
    print("Successfully added realistic matches!")
