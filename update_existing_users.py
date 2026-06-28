from app import create_app
from models import db, User, Prediction
import random

app = create_app()

with app.app_context():
    users = User.query.filter(User.id < 10000).all()
    for user in users:
        old_id = user.id
        
        while True:
            new_id = random.randint(10000, 99999)
            if not User.query.get(new_id):
                break
                
        print(f"Updating {user.name} from {old_id} to {new_id}")
        
        db.session.execute(db.text(f"UPDATE predictions SET user_id = {new_id} WHERE user_id = {old_id}"))
        db.session.execute(db.text(f"UPDATE users SET id = {new_id} WHERE id = {old_id}"))
        
    db.session.commit()
    print("All existing users updated to random 5-digit IDs!")
