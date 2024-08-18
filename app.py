import os
from base64 import b64encode
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, get_flashed_messages
from backend.employee_management import fetch_employees, fetch_employee_details, delete_employee, update_employee, add_employee
from backend.company_management import fetch_companies, fetch_company_by_name, fetch_company_by_color, add_company, fetch_company_stats, update_company, delete_company
from backend.project_management import create_project, fetch_projects, update_project, delete_project, fetch_employees_by_companies, link_employees_to_project, fetch_filtered_projects
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

@app.route('/companies_dashboard')
def companies_dashboard():
    companies = fetch_companies()
    company_stats = {company['id']: fetch_company_stats(company['id']) for company in companies}
    return render_template('companies_dashboard.html', companies=companies, company_stats=company_stats)

@app.route('/update_company', methods=['POST'])
def update_company_route():
    company_id = request.form['id']
    name = request.form['name']
    color = request.form['color']
    existing_company = fetch_company_by_name(name)
    existing_color = fetch_company_by_color(color)
    if (existing_company and existing_company['id'] != int(company_id)) or (existing_color and existing_color['id'] != int(company_id)):
        return jsonify({'success': False, 'message': 'Company name or color already exists.'})
    update_company(company_id, name, color)
    return jsonify({'success': True})

@app.route('/delete_company', methods=['POST'])
def delete_company_route():
    company_id = request.form['id']
    delete_company(company_id)
    return redirect(url_for('companies_dashboard'))

@app.route('/add_company', methods=['POST'])
def add_company_route():
    name = request.form['name']
    color = request.form['color']
    existing_company = fetch_company_by_name(name)
    existing_color = fetch_company_by_color(color)
    if existing_company or existing_color:
        return jsonify({'success': False, 'message': 'Company name or color already exists.'})
    add_company(name, color)
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
    salary = request.form['salary']
    date_of_birth = request.form['date_of_birth']
    job_title = request.form['job_title']
    employment_status = request.form['employment_status']
    update_employee(employee_id, fname, lname, company, address, city, county, color, photo, salary, date_of_birth, job_title, employment_status)
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
    salary = request.form['salary']
    date_of_birth = request.form['date_of_birth']
    job_title = request.form['job_title']
    employment_status = request.form['employment_status']
    add_employee(fname, lname, company, address, city, county, color, photo, salary, date_of_birth, job_title, employment_status)
    return jsonify({'success': True})

@app.route('/projects')
def projects():
    projects = fetch_projects()
    companies = fetch_companies()
    employees = fetch_employees()
    return render_template('projects.html', projects=projects, companies=companies, employees=employees)

@app.route('/fetch_filtered_projects', methods=['POST'])
def fetch_filtered_projects_route():
    date_range = request.json.get('date_range', {})
    company_ids = request.json.get('company_ids', [])
    statistic = request.json.get('statistic', 'most_expensive')
    
    projects = fetch_filtered_projects(date_range, company_ids, statistic)
    return jsonify(projects)

@app.route('/add_project', methods=['POST'])
def add_project_route():
    name = request.form['name']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    budget = request.form['budget']
    time_estimation = request.form['time_estimation']
    company_ids = request.form.getlist('companies')
    result = create_project(name, description, start_date, end_date, budget, time_estimation, company_ids)
    return jsonify(result)

@app.route('/update_project', methods=['POST'])
def update_project_route():
    project_id = request.form['id']
    name = request.form['name']
    description = request.form['description']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    budget = request.form['budget']
    time_estimation = request.form['time_estimation']
    company_ids = request.form.getlist('companies')
    result = update_project(project_id, name, description, start_date, end_date, budget, time_estimation, company_ids)
    return jsonify(result)

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project_route(project_id):
    result = delete_project(project_id)
    return jsonify(result)

@app.route('/fetch_employees_by_companies', methods=['POST'])
def fetch_employees_by_companies_route():
    company_ids = request.json.get('company_ids', [])
    employees = fetch_employees_by_companies(company_ids)
    return jsonify({'employees': employees})

@app.route('/link_employees_to_project', methods=['POST'])
def link_employees_to_project_route():
    project_id = request.form['project_id']
    employee_ids = request.form.getlist('employees')
    result = link_employees_to_project(project_id, employee_ids)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)