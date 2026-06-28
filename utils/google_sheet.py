import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

class GoogleSheetSync:
    _sheet_id = '13fTBNtuSCDvcofAjFyKysAuMTJ-7ZToAC0MJXo0FymY'
    _client = None
    _spreadsheet = None
    
    @classmethod
    def get_spreadsheet(cls):
        if cls._spreadsheet is not None:
            return cls._spreadsheet
            
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials.json')
            
            if not os.path.exists(creds_path):
                print("[Sheet Sync ERROR] credentials.json not found! Cannot sync.")
                return None
                
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            cls._client = gspread.authorize(creds)
            cls._spreadsheet = cls._client.open_by_key(cls._sheet_id)
            return cls._spreadsheet
        except Exception as e:
            print(f"[Sheet Sync ERROR] Failed to connect: {e}")
            return None

    @classmethod
    def _get_or_create_worksheet(cls, title, headers=None):
        sheet = cls.get_spreadsheet()
        if not sheet:
            return None
            
        try:
            worksheet = sheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=title, rows="1000", cols="20")
            if headers:
                worksheet.append_row(headers)
        return worksheet

    @classmethod
    def _upsert_row(cls, worksheet, row_data):
        try:
            record_id = str(row_data[0])
            cell = worksheet.find(record_id, in_column=1)
            # If found, update the row
            row_idx = cell.row
            
            # Use ASCII math to get end column letter, e.g. A to I
            end_col = chr(64 + len(row_data))
            if len(row_data) > 26:
                 end_col = 'Z' # simplification for our small tables
                 
            worksheet.update(f"A{row_idx}:{end_col}{row_idx}", [row_data])
        except gspread.exceptions.CellNotFound:
            worksheet.append_row(row_data)
        except Exception as e:
            print(f"[Sheet Sync ERROR] Upsert failed: {e}")

    @staticmethod
    def sync_user(user):
        worksheet = GoogleSheetSync._get_or_create_worksheet("Users", ["ID", "Name", "Mobile", "Email", "District", "State", "Referral Code", "Points", "Registered At"])
        if worksheet:
            GoogleSheetSync._upsert_row(worksheet, [user.id, user.name, user.mobile, user.email, user.district, user.state, user.referral_code, user.points, str(user.created_at)])
        
    @staticmethod
    def sync_match(match):
        worksheet = GoogleSheetSync._get_or_create_worksheet("Matches", ["ID", "Home Team", "Away Team", "Kickoff Time", "Venue", "Status"])
        if worksheet:
            GoogleSheetSync._upsert_row(worksheet, [match.id, match.home_team, match.away_team, str(match.kickoff_time), match.venue, match.status])
        
    @staticmethod
    def sync_prediction(prediction):
        worksheet = GoogleSheetSync._get_or_create_worksheet("Predictions", ["ID", "User ID", "User Name", "Mobile", "Match ID", "Winner", "Home Score", "Away Score", "Points Awarded", "Status"])
        if worksheet:
            user_name = prediction.user.name if prediction.user else ""
            user_mobile = prediction.user.mobile if prediction.user else ""
            GoogleSheetSync._upsert_row(worksheet, [prediction.id, prediction.user_id, user_name, user_mobile, prediction.match_id, prediction.winner, prediction.home_score, prediction.away_score, prediction.points_awarded, prediction.status])
        
    @staticmethod
    def sync_result(match):
        worksheet = GoogleSheetSync._get_or_create_worksheet("Results", ["Match ID", "Home Team", "Away Team", "Home Score", "Away Score", "Status"])
        if worksheet:
            GoogleSheetSync._upsert_row(worksheet, [match.id, match.home_team, match.away_team, match.home_score, match.away_score, match.status])
        
    @staticmethod
    def log_action(action):
        worksheet = GoogleSheetSync._get_or_create_worksheet("Logs", ["Timestamp", "Action"])
        if worksheet:
            try:
                worksheet.append_row([str(datetime.utcnow()), action])
                print(f"[Sheet Sync LOG] {action}")
            except Exception as e:
                print(f"[Sheet Sync ERROR] {e}")

    @classmethod
    def sync_down(cls):
        from models import db, User, Match, Prediction
        sheet = cls.get_spreadsheet()
        if not sheet:
            return "Failed to connect to Google Sheets."
            
        logs = []
        
        # Sync Users
        try:
            ws = sheet.worksheet("Users")
            records = ws.get_all_records()
            sheet_user_ids = [str(r.get('ID', '')) for r in records if r.get('ID')]
            
            db_users = User.query.all()
            for user in db_users:
                if str(user.id) not in sheet_user_ids:
                    db.session.delete(user)
                    logs.append(f"Deleted User {user.id}")
        except Exception:
            pass
            
        # Sync Matches
        try:
            ws = sheet.worksheet("Matches")
            records = ws.get_all_records()
            sheet_match_ids = [str(r.get('ID', '')) for r in records if r.get('ID')]
            
            db_matches = Match.query.all()
            for match in db_matches:
                if str(match.id) not in sheet_match_ids:
                    db.session.delete(match)
                    logs.append(f"Deleted Match {match.id}")
        except Exception:
            pass
            
        # Sync Predictions
        try:
            ws = sheet.worksheet("Predictions")
            records = ws.get_all_records()
            sheet_pred_ids = [str(r.get('ID', '')) for r in records if r.get('ID')]
            
            db_preds = Prediction.query.all()
            for pred in db_preds:
                if str(pred.id) not in sheet_pred_ids:
                    db.session.delete(pred)
                    logs.append(f"Deleted Prediction {pred.id}")
        except Exception:
            pass
            
        db.session.commit()
        return "Synced down successfully. " + ", ".join(logs)
