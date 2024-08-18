from .database import get_connection

def fetch_companies():
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, name, color FROM Companies")
    companies = cursor.fetchall()
    cursor.close()
    mydb.close()
    return companies

def fetch_company_by_name(name):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, color FROM Companies WHERE name = %s", (name,))
    company = cursor.fetchone()
    cursor.close()
    mydb.close()
    return company

def fetch_company_by_color(color):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM Companies WHERE color = %s", (color,))
    company = cursor.fetchone()
    cursor.close()
    mydb.close()
    return company

def fetch_company_stats(company_id):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT 
        COUNT(*) as employee_count, 
        GROUP_CONCAT(CONCAT(gps_location, ',', fname, ' ', lname)) as gps_locations 
    FROM Employees 
    WHERE company_id = %s AND isDeleted = FALSE
    """, (company_id,))
    stats = cursor.fetchone()
    cursor.close()
    mydb.close()
    return stats

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

def delete_company(company_id):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Employees WHERE company_id = %s", (company_id,))
    cursor.execute("DELETE FROM Companies WHERE id = %s", (company_id,))
    mydb.commit()
    cursor.close()
    mydb.close()