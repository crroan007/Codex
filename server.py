import os
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2 import service_account
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)

# Enable CORS for your frontend
CORS(app, resources={r"/*": {"origins": "https://codex.college"}})

# Google Sheets Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_info({
        "type": "service_account",
        "project_id": os.environ.get('GOOGLE_PROJECT_ID'),
        "private_key_id": os.environ.get('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": os.environ.get('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.environ.get('GOOGLE_CLIENT_EMAIL'),
        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('GOOGLE_CLIENT_X509_CERT_URL')
    }, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

# Health check endpoint to wake the backend
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Submissions').execute()
        values = result.get('values', [])
        submissions = []
        if values:
            headers = values[0]
            for row in values[1:]:
                submission = dict(zip(headers, row))
                submissions.append(submission)
        return jsonify({'status': 'success', 'submissions': submissions})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        values = [[data['id'], data['url'], data['priority'], data['submitterEmail'], data['timestamp']]]
        body = {'values': values}
        sheet.values().append(spreadsheetId=GOOGLE_SHEET_ID, range='Submissions', valueInputOption='RAW', body=body).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/activity', methods=['POST'])
def add_activity():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        values = [[data['userEmail'], data['submissionId'], data['status'], data['timestamp'], data['month']]]
        body = {'values': values}
        sheet.values().append(spreadsheetId=GOOGLE_SHEET_ID, range='Activity', valueInputOption='RAW', body=body).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/activity', methods=['GET'])
def get_activity():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Activity').execute()
        values = result.get('values', [])
        activity = []
        if values:
            headers = values[0]
            for row in values[1:]:
                entry = dict(zip(headers, row))
                activity.append(entry)
        return jsonify({'status': 'success', 'activity': activity})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Users').execute()
        values = result.get('values', [])
        users = []
        if values:
            headers = values[0]
            for row in values[1:]:
                user = dict(zip(headers, row))
                users.append(user)
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        values = [[data['email'], data['points'], data['title']]]
        body = {'values': values}
        sheet.values().append(spreadsheetId=GOOGLE_SHEET_ID, range='Users', valueInputOption='RAW', body=body).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/users/update', methods=['POST'])
def update_user():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Users').execute()
        values = result.get('values', [])
        if not values:
            return jsonify({'status': 'error', 'message': 'Users sheet is empty'}), 404
        headers = values[0]
        rows = values[1:]
        row_index = None
        for i, row in enumerate(rows):
            if row[0] == data['email']:
                row_index = i + 2  # Account for header row and 1-based indexing
                break
        if row_index is None:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        update_values = [[data['email'], data['points'], data.get('title', '')]]
        sheet.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'Users!A{row_index}:C{row_index}',
            valueInputOption='RAW',
            body={'values': update_values}
        ).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Leaderboard').execute()
        values = result.get('values', [])
        leaderboard = []
        if values:
            headers = values[0]
            for row in values[1:]:
                entry = dict(zip(headers, row))
                leaderboard.append(entry)
        return jsonify({'status': 'success', 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard', methods=['POST'])
def add_leaderboard():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        values = [[data['userEmail'], data['month'], data['points'], data['title']]]
        body = {'values': values}
        sheet.values().append(spreadsheetId=GOOGLE_SHEET_ID, range='Leaderboard', valueInputOption='RAW', body=body).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leaderboard/update', methods=['POST'])
def update_leaderboard():
    try:
        data = request.get_json()
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Leaderboard').execute()
        values = result.get('values', [])
        if not values:
            return jsonify({'status': 'error', 'message': 'Leaderboard sheet is empty'}), 404
        headers = values[0]
        rows = values[1:]
        row_index = None
        for i, row in enumerate(rows):
            if row[0] == data['userEmail'] and row[1] == data['month']:
                row_index = i + 2  # Account for header row and 1-based indexing
                break
        if row_index is None:
            return jsonify({'status': 'error', 'message': 'Leaderboard entry not found'}), 404
        update_values = [[data['userEmail'], data['month'], data['points'], data.get('title', '')]]
        sheet.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'Leaderboard!A{row_index}:D{row_index}',
            valueInputOption='RAW',
            body={'values': update_values}
        ).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
