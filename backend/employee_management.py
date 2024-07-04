from .database import get_connection

def fetch_employees(companies=None, search_text='', sort_state=0, page=1, items_per_page=10):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    query = """
    SELECT Employees.id, Employees.fname, Employees.lname, Companies.name as company, Employees.photo, Employees.color 
    FROM Employees 
    JOIN Companies ON Employees.company_id = Companies.id 
    WHERE 1=1
    """
    params = []

    if companies:
        format_strings = ','.join(['%s'] * len(companies))
        query += " AND Companies.name IN (%s)" % format_strings
        params.extend(companies)

    if search_text:
        query += " AND (LOWER(Employees.fname) LIKE %s OR LOWER(Employees.lname) LIKE %s)"
        params.extend([f"{search_text}%", f"{search_text}%"])

    if sort_state == 1:
        query += " ORDER BY Employees.fname ASC, Employees.lname ASC"
    elif sort_state == 2:
        query += " ORDER BY Employees.fname DESC, Employees.lname DESC"
    
    cursor.execute(query, tuple(params))
    total_employees = len(cursor.fetchall())
    
    offset = (page - 1) * items_per_page
    query += " LIMIT %s OFFSET %s"
    params.extend([items_per_page, offset])

    cursor.execute(query, tuple(params))
    employees = cursor.fetchall()
    
    cursor.close()
    mydb.close()
    return employees, total_employees

def fetch_companies():
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, name, color FROM Companies")
    companies = cursor.fetchall()
    cursor.close()
    mydb.close()
    return companies

def add_company(name, color):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO Companies (name, color) VALUES (%s, %s)", (name, color))
    mydb.commit()
    cursor.close()
    mydb.close()

def update_company(company_id, name, color):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("UPDATE Companies SET name = %s, color = %s WHERE id = %s", (name, color, company_id))
    cursor.execute("UPDATE Employees SET color = %s WHERE company_id = %s", (color, company_id))
    mydb.commit()
    cursor.close()
    mydb.close()

def fetch_company_by_name(name):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, color FROM Companies WHERE name = %s", (name,))
    company = cursor.fetchone()
    cursor.close()
    mydb.close()
    return company

def delete_company(company_id):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Employees WHERE company_id = %s", (company_id,))
    cursor.execute("DELETE FROM Companies WHERE id = %s", (company_id,))
    mydb.commit()
    cursor.close()
    mydb.close()

def fetch_employee_details(employee_id):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT Employees.id, Employees.fname, Employees.lname, Companies.name as company, Employees.address, Employees.city, Employees.county, Employees.color, Employees.photo 
    FROM Employees 
    JOIN Companies ON Employees.company_id = Companies.id 
    WHERE Employees.id = %s
    """, (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    mydb.close()
    return employee

def delete_employee(employee_id):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Employees WHERE id = %s", (employee_id,))
    mydb.commit()
    cursor.close()
    mydb.close()
    
def update_employee(employee_id, fname, lname, company, address, city, county, color, photo):
    mydb = get_connection()
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            UPDATE Employees
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s, photo = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, photo_data, employee_id))
    else:
        cursor.execute("""
            UPDATE Employees
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, employee_id))
    mydb.commit()
    cursor.close()

def add_employee(fname, lname, company, address, city, county, color, photo):
    mydb = get_connection()
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            INSERT INTO Employees (fname, lname, company_id, address, city, county, color, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color, photo_data))
    else:
        cursor.execute("""
            INSERT INTO Employees (fname, lname, company_id, address, city, county, color)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color))
    mydb.commit()
    cursor.close()
    mydb.close()
