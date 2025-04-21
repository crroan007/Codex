from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

app = Flask(__name__)
# Allow CORS for your GitHub Pages origin
CORS(app, resources={r"/*": {"origins": "https://crroan007.github.io"}})

# Load service account credentials from environment variable
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
credentials_info = json.loads(GOOGLE_CREDENTIALS)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1eM2HCV5xFvaAu-o5BGHsXw9NC64N7BjIhe0ZrNP-sXk'  # Replace with your Google Sheet ID

# Authenticate with Google Sheets API using the service account
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        values = [[
            data['id'],
            data['url'],
            data['priority'],
            data['submitterEmail'],
            data['timestamp']
        ]]
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Submissions!A:E',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Submissions!A2:E'
        ).execute()
        values = result.get('values', [])
        submissions = [
            {
                'id': int(row[0]),
                'url': row[1],
                'priority': int(row[2]),
                'submitterEmail': row[3],
                'timestamp': row[4]
            } for row in values
        ]
        return jsonify({'status': 'success', 'submissions': submissions})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/activity', methods=['POST'])
def add_activity():
    try:
        data = request.get_json()
        values = [[
            data['userEmail'],
            data['submissionId'],
            data['status'],
            data['timestamp'],
            data['month']
        ]]
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Activity!A:E',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/activity', methods=['GET'])
def get_activity():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Activity!A2:E'
        ).execute()
        values = result.get('values', [])
        activity = [
            {
                'userEmail': row[0],
                'submissionId': int(row[1]),
                'status': row[2],
                'timestamp': row[3],
                'month': row[4]
            } for row in values
        ]
        return jsonify({'status': 'success', 'activity': activity})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        values = [[
            data['email'],
            data['points'],
            data['title']
        ]]
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Users!A:C',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Users!A2:C'
        ).execute()
        values = result.get('values', [])
        users = [
            {
                'email': row[0],
                'points': int(row[1]),
                'title': row[2]
            } for row in values
        ]
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users/update', methods=['POST'])
def update_user_points():
    try:
        data = request.get_json()
        email = data['email']
        points = data['points']
        title = data.get('title', '')
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Users!A2:C'
        ).execute()
        values = result.get('values', [])
        row_index = next((i for i, row in enumerate(values) if row[0] == email), -1) + 2
        if row_index == 1:  # No user found (row_index 1 means no match, as we add 2)
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Users!B{row_index}',
            valueInputOption='RAW',
            body={'values': [[points]]}
        ).execute()
        if title:
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Users!C{row_index}',
                valueInputOption='RAW',
                body={'values': [[title]]}
            ).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard', methods=['POST'])
def add_leaderboard_entry():
    try:
        data = request.get_json()
        values = [[
            data['userEmail'],
            data['month'],
            data['points'],
            data.get('title', '')
        ]]
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Leaderboard!A:D',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Leaderboard!A2:D'
        ).execute()
        values = result.get('values', [])
        leaderboard = [
            {
                'userEmail': row[0],
                'month': row[1],
                'points': int(row[2]),
                'title': row[3]
            } for row in values
        ]
        return jsonify({'status': 'success', 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard/update', methods=['POST'])
def update_leaderboard_entry():
    try:
        data = request.get_json()
        user_email = data['userEmail']
        month = data['month']
        points = data['points']
        title = data.get('title', '')
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Leaderboard!A2:D'
        ).execute()
        values = result.get('values', [])
        row_index = next((i for i, row in enumerate(values) if row[0] == user_email and row[1] == month), -1) + 2
        if row_index == 1:  # No entry found
            return jsonify({'status': 'error', 'message': 'Leaderboard entry not found'}), 404
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Leaderboard!C{row_index}',
            valueInputOption='RAW',
            body={'values': [[points]]}
        ).execute()
        if title:
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Leaderboard!D{row_index}',
                valueInputOption='RAW',
                body={'values': [[title]]}
            ).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/reset_leaderboard', methods=['POST'])
def reset_leaderboard():
    try:
        # Get current month
        from datetime import datetime
        current_month = datetime.utcnow().strftime('%Y-%m')
        # Get all leaderboard entries
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Leaderboard!A2:D'
        ).execute()
        values = result.get('values', [])
        # Filter out entries for the current month
        new_values = [row for row in values if row[1] != current_month]
        # Clear the Leaderboard tab and rewrite entries (excluding current month)
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range='Leaderboard!A2:D'
        ).execute()
        if new_values:
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='Leaderboard!A2:D',
                valueInputOption='RAW',
                body={'values': new_values}
            ).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)