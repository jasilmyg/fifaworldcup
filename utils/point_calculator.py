from datetime import datetime, timedelta

def calculate_prediction_points(prediction, match):
    """
    Calculates points based on the rules:
    Correct Winner: +10
    Correct Draw: +10
    Correct Goal Difference: +8
    Correct Exact Score: +25
    Prediction before 24 Hours: Bonus +3
    Prediction before 48 Hours: Bonus +5
    """
    points = 0
    
    actual_home = match.home_score
    actual_away = match.away_score
    pred_home = prediction.home_score
    pred_away = prediction.away_score
    
    # Determine actual winner
    if actual_home > actual_away:
        actual_winner = 'home'
    elif actual_away > actual_home:
        actual_winner = 'away'
    else:
        actual_winner = 'draw'
        
    # Exact Score
    if actual_home == pred_home and actual_away == pred_away:
        points += 25
    else:
        # Correct Winner or Draw
        if prediction.winner == actual_winner:
            points += 10
            
            # Goal difference check (only if not exact score)
            actual_diff = actual_home - actual_away
            pred_diff = pred_home - pred_away
            if actual_diff == pred_diff:
                points += 8


    return points
