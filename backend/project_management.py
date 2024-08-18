from .database import get_connection

def fetch_filtered_projects(date_range=None, company_ids=None, statistic=None):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)

    query = """
    SELECT p.*, 
           GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ') as companies, 
           GROUP_CONCAT(DISTINCT CONCAT(e.fname, ' ', e.lname) SEPARATOR ', ') as employees,
           DATEDIFF(p.end_date, p.start_date) as duration,
           COUNT(DISTINCT pe.employee_id) as employee_count
    FROM Projects p
    LEFT JOIN ProjectCompanies pc ON p.id = pc.project_id
    LEFT JOIN Companies c ON pc.company_id = c.id
    LEFT JOIN ProjectEmployees pe ON p.id = pe.project_id
    LEFT JOIN Employees e ON pe.employee_id = e.id
    WHERE 1=1
    """

    params = []

    if date_range:
        start_date, end_date = date_range

        if start_date and start_date != 'start':
            query += " AND p.start_date >= %s"
            params.append(start_date)
        if end_date and end_date != 'end':
            query += " AND p.end_date <= %s"
            params.append(end_date)

    if company_ids:
        query += " AND c.id IN (%s)" % ','.join(['%s'] * len(company_ids))
        params.extend(company_ids)

    query += " GROUP BY p.id"
    
    if statistic == 'budget':
        query += " ORDER BY p.budget DESC"
    elif statistic == 'duration':
        query += " ORDER BY duration DESC"
    elif statistic == 'employees':
        query += " ORDER BY employee_count DESC"

    cursor.execute(query, params)
    projects = cursor.fetchall()

    cursor.close()
    mydb.close()

    for project in projects:
        project['companies'] = project['companies'].split(', ') if project['companies'] else []
        project['employees'] = project['employees'].split(', ') if project['employees'] else []

    return projects

def create_project(name, description, start_date, end_date, budget, time_estimation, company_ids):
    mydb = get_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT id FROM Projects WHERE name = %s", (name,))
    if cursor.fetchone():
        cursor.close()
        mydb.close()
        return {'success': False, 'message': 'Project name already exists.'}

    cursor.execute("""
    INSERT INTO Projects (name, description, start_date, end_date, budget, time_estimation)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, description, start_date, end_date, budget, time_estimation))
    project_id = cursor.lastrowid

    for company_id in company_ids:
        cursor.execute("""
        INSERT INTO ProjectCompanies (project_id, company_id)
        VALUES (%s, %s)
        """, (project_id, company_id))

    mydb.commit()
    cursor.close()
    mydb.close()
    return {'success': True}

def fetch_projects():
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("""
    SELECT p.*, 
           GROUP_CONCAT(DISTINCT c.name SEPARATOR ', ') as companies, 
           GROUP_CONCAT(DISTINCT CONCAT(e.fname, ' ', e.lname) SEPARATOR ', ') as employees,
           GROUP_CONCAT(DISTINCT c.id SEPARATOR ',') as company_ids,
           GROUP_CONCAT(DISTINCT pe.employee_id SEPARATOR ',') as employee_ids
    FROM Projects p
    LEFT JOIN ProjectCompanies pc ON p.id = pc.project_id
    LEFT JOIN Companies c ON pc.company_id = c.id
    LEFT JOIN ProjectEmployees pe ON p.id = pe.project_id
    LEFT JOIN Employees e ON pe.employee_id = e.id
    GROUP BY p.id
    """)
    projects = cursor.fetchall()

    cursor.close()
    mydb.close()

    for project in projects:
        project['company_ids'] = project['company_ids'].split(',') if project['company_ids'] else []
        project['employee_ids'] = project['employee_ids'].split(',') if project['employee_ids'] else []
        project['employees'] = project['employees'].split(', ') if project['employees'] else []

    return projects

def update_project(project_id, name, description, start_date, end_date, budget, time_estimation, company_ids):
    mydb = get_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT id FROM Projects WHERE name = %s AND id != %s", (name, project_id))
    if cursor.fetchone():
        cursor.close()
        mydb.close()
        return {'success': False, 'message': 'Project name already exists.'}

    cursor.execute("""
    UPDATE Projects
    SET name = %s, description = %s, start_date = %s, end_date = %s, budget = %s, time_estimation = %s
    WHERE id = %s
    """, (name, description, start_date, end_date, budget, time_estimation, project_id))

    cursor.execute("DELETE FROM ProjectCompanies WHERE project_id = %s", (project_id,))
    for company_id in company_ids:
        cursor.execute("""
        INSERT INTO ProjectCompanies (project_id, company_id)
        VALUES (%s, %s)
        """, (project_id, company_id))

    mydb.commit()
    cursor.close()
    mydb.close()
    return {'success': True}

def delete_project(project_id):
    mydb = get_connection()
    cursor = mydb.cursor()

    cursor.execute("DELETE FROM ProjectCompanies WHERE project_id = %s", (project_id,))
    cursor.execute("DELETE FROM ProjectEmployees WHERE project_id = %s", (project_id,))
    cursor.execute("DELETE FROM Projects WHERE id = %s", (project_id,))

    mydb.commit()
    cursor.close()
    mydb.close()
    return {'success': True}

def fetch_employees_by_companies(company_ids):
    if not company_ids:
        return []

    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    
    query = """
    SELECT Employees.id, Employees.fname, Employees.lname, Companies.name as company
    FROM Employees
    JOIN Companies ON Employees.company_id = Companies.id
    WHERE Employees.isDeleted = FALSE
    AND Employees.company_id IN (%s)
    """ % ','.join(['%s'] * len(company_ids))

    cursor.execute(query, tuple(company_ids))
    employees = cursor.fetchall()

    cursor.close()
    mydb.close()

    return employees


def link_employees_to_project(project_id, employee_ids):
    mydb = get_connection()
    cursor = mydb.cursor()

    cursor.execute("DELETE FROM ProjectEmployees WHERE project_id = %s", (project_id,))
    for employee_id in employee_ids:
        cursor.execute("""
        INSERT INTO ProjectEmployees (project_id, employee_id)
        VALUES (%s, %s)
        """, (project_id, employee_id))

    mydb.commit()
    cursor.close()
    mydb.close()
    return {'success': True}
