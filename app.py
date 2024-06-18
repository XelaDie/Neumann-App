from flask import Flask, render_template, request, redirect, url_for, jsonify
from base64 import b64encode
from backend.user_management import fetch_users, fetch_companies, fetch_user_details, delete_user

app = Flask(__name__)

def convert_bytes_to_str(data):
    if isinstance(data, bytes):
        return b64encode(data).decode('utf-8')
    elif isinstance(data, dict):
        return {k: convert_bytes_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_bytes_to_str(i) for i in data]
    else:
        return data

@app.template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return b64encode(data).decode('utf-8')
    return None

@app.route('/')
def index():
    users = fetch_users()
    companies = fetch_companies()
    return render_template('index.html', users=users, companies=companies)

@app.route('/filter_users', methods=['POST'])
def filter_users():
    selected_companies = request.json.get('companies', [])
    users = fetch_users(selected_companies)
    json_compatible_users = convert_bytes_to_str(users)
    return jsonify(json_compatible_users)

@app.route('/user/<int:user_id>')
def user_details(user_id):
    user = fetch_user_details(user_id)
    if user.get('photo'):
        user['photo'] = b64encode(user['photo']).decode('utf-8')
    return jsonify(user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    delete_user(user_id)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)