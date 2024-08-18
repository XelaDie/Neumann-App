from .database import get_connection
from .company_management import fetch_company_by_name
from geopy.geocoders import Nominatim

def get_gps_location(address):
    geolocator = Nominatim(user_agent="employee_management")
    try: 
        location = geolocator.geocode(address)
        return f"{location.latitude},{location.longitude}"
    except: return None

def fetch_employees(companies=None, search_text='', sort_state=0, page=1, items_per_page=10):
    mydb = get_connection()
    cursor = mydb.cursor(dictionary=True)
    query = """
    SELECT Employees.id, Employees.fname, Employees.lname, Companies.name as company, Employees.photo, Employees.color 
    FROM Employees 
    JOIN Companies ON Employees.company_id = Companies.id 
    WHERE Employees.isDeleted = FALSE
    """
    params = []

    if companies:
        format_strings = ','.join(['%s'] * len(companies))
        query += " AND Companies.name IN (%s)" % format_strings
        params.extend(companies)

    if search_text:
        query += " AND (LOWER(Employees.fname) LIKE %s OR LOWER(Employees.lname) LIKE %s)"
        params.extend([f"%{search_text}%", f"%{search_text}%"])

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

def fetch_employee_details(employee_id):
  mydb = get_connection()
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("""
  SELECT 
      Employees.id, 
      Employees.fname, 
      Employees.lname, 
      Companies.name as company, 
      Employees.address, 
      Employees.city,
      Employees.county, 
      Employees.color,
      Employees.photo,
      Employees.gps_location,
      DATE_FORMAT(Employees.date_account_created, '%d %b %Y') as date_account_created,
      Employees.salary,
      DATE_FORMAT(Employees.date_of_birth, '%d %b %Y') as date_of_birth,
      Employees.job_title,
      Employees.employment_status
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
    cursor.execute("UPDATE Employees SET isDeleted = TRUE WHERE id = %s", (employee_id,))
    mydb.commit()
    cursor.close()
    mydb.close()
    
def update_employee(employee_id, fname, lname, company, address, city, county, color, photo, salary, date_of_birth, job_title, employment_status):
    gps_location = get_gps_location(f"{county}, {city}, {address}")
    mydb = get_connection()
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            UPDATE Employees
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s, photo = %s, gps_location= %s, salary = %s, date_of_birth = %s, job_title = %s, employment_status = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, photo_data, gps_location, salary, date_of_birth, job_title, employment_status, employee_id))
    else:
        cursor.execute("""
            UPDATE Employees
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s, gps_location= %s, salary = %s, date_of_birth = %s, job_title = %s, employment_status = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, gps_location, salary, date_of_birth, job_title, employment_status, employee_id))
    mydb.commit()
    cursor.close()
    mydb.close()

def add_employee(fname, lname, company, address, city, county, color, photo, salary, date_of_birth, job_title, employment_status):
    gps_location = get_gps_location(f"{county}, {city}, {address}")
    mydb = get_connection()
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            INSERT INTO Employees (fname, lname, company_id, address, city, county, color, photo, gps_location, salary, date_of_birth, job_title, employment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color, photo_data, gps_location, salary, date_of_birth, job_title, employment_status))
    else:
        cursor.execute("""
            INSERT INTO Employees (fname, lname, company_id, address, city, county, color, gps_location, salary, date_of_birth, job_title, employment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color, gps_location, salary, date_of_birth, job_title, employment_status))
    mydb.commit()
    cursor.close()
    mydb.close()
