import os
from datetime import timedelta
from base64 import b64encode
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, get_flashed_messages
from backend.employee_management import fetch_employees, fetch_companies, fetch_employee_details, delete_employee, update_employee, add_employee
from backend.employee_management import add_company, update_company, delete_company
from backend.user_management import signup_user, confirm_signup, login_user, forgot_password, reset_password, logout_user

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
    if 'username' in session:
        employees = fetch_employees()
        companies = fetch_companies()
        return render_template('index.html', employees=employees, companies=companies)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if signup_user(username, email, password):
            flash('Signup successful! Please check your email to confirm your account.', 'success')
            return render_template('confirm.html', messages=get_flashed_messages(with_categories=True))
        return render_template('signup.html', messages=get_flashed_messages(with_categories=True))
    return render_template('signup.html', messages=get_flashed_messages(with_categories=True))

@app.route('/confirm', methods=['POST'])
def confirm():
    code = request.form['code']
    if confirm_signup(code):
        flash('Confirmation successful! Please log in.', 'success')
        return redirect(url_for('login', messages=get_flashed_messages(with_categories=True)))
    return render_template('confirm.html', messages=get_flashed_messages(with_categories=True))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_user(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        return render_template('login.html', messages=get_flashed_messages(with_categories=True))
    return render_template('login.html', messages=get_flashed_messages(with_categories=True))

@app.route('/forgot_password', methods=['POST'])
def forgot_password_route():
    email = request.form['email']
    if forgot_password(email):
        flash('Password reset email sent. Please check your email.', 'success')
        return render_template('reset_password.html', messages=get_flashed_messages(with_categories=True))
    return render_template('login.html', messages=get_flashed_messages(with_categories=True))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_route():
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']
        if reset_password(code, new_password):
            flash('Password reset successful! Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('reset_password.html', messages=get_flashed_messages(with_categories=True))
    return render_template('reset_password.html', messages=get_flashed_messages(with_categories=True))

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login', messages=get_flashed_messages(with_categories=True)))

@app.route('/filter_employees', methods=['POST'])
def filter_employees():
    selected_companies = request.json.get('companies', [])
    search_text = request.json.get('searchText', '').lower()
    sort_state = request.json.get('sortState', 0)
    page = request.json.get('page', 1)
    items_per_page = request.json.get('itemsPerPage', 10)
    employees, total_employees = fetch_employees(selected_companies, search_text, sort_state, page, items_per_page)
    json_compatible_employees = convert_bytes_to_str(employees)
    return jsonify({'employees': json_compatible_employees, 'totalEmployees': total_employees})

@app.route('/companies', methods=['GET'])
def get_companies():
    companies = fetch_companies()
    return jsonify(companies)

@app.route('/add_company', methods=['POST'])
def add_company_route():
    name = request.form['name']
    color = request.form['color']
    add_company(name, color)
    return jsonify({'success': True})

@app.route('/update_company', methods=['POST'])
def update_company_route():
    company_id = request.form['id']
    name = request.form['name']
    color = request.form['color']
    update_company(company_id, name, color)
    return jsonify({'success': True})

@app.route('/delete_company', methods=['POST'])
def delete_company_route():
    company_id = request.form['id']
    delete_company(company_id)
    return jsonify({'success': True})

@app.route('/employee/<int:employee_id>')
def employee_details(employee_id):
    employee = fetch_employee_details(employee_id)
    if employee.get('photo'):
        employee['photo'] = b64encode(employee['photo']).decode('utf-8')
    return jsonify(employee)

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee_route(employee_id):
    delete_employee(employee_id)
    return jsonify({'success': True})

@app.route('/update_employee', methods=['POST'])
def update_employee_route():
    employee_id = request.form['employee_id']
    fname = request.form['fname']
    lname = request.form['lname']
    company = request.form['company']
    address = request.form['address']
    city = request.form['city']
    county = request.form['county']
    color = request.form['color']
    photo = request.files.get('photo')
    update_employee(employee_id, fname, lname, company, address, city, county, color, photo)
    return jsonify({'success': True})

@app.route('/add_employee', methods=['POST'])
def add_employee_route():
    fname = request.form['fname']
    lname = request.form['lname']
    company = request.form['company']
    address = request.form['address']
    city = request.form['city']
    county = request.form['county']
    color = request.form['color']
    photo = request.files.get('photo')
    add_employee(fname, lname, company, address, city, county, color, photo)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)