from .database import mydb

def fetch_users(companies=None, search_text='', sort_state=0):
    cursor = mydb.cursor(dictionary=True)
    query = """
    SELECT Users.id, Users.fname, Users.lname, Companies.name as company, Users.photo, Users.color 
    FROM Users 
    JOIN Companies ON Users.company_id = Companies.id 
    WHERE 1=1
    """
    params = []

    if companies:
        format_strings = ','.join(['%s'] * len(companies))
        query += " AND Companies.name IN (%s)" % format_strings
        params.extend(companies)

    if search_text:
        query += " AND (LOWER(Users.fname) LIKE %s OR LOWER(Users.lname) LIKE %s)"
        params.extend([f"{search_text}%", f"{search_text}%"])

    if sort_state == 1:
        query += " ORDER BY Users.fname ASC, Users.lname ASC"
    elif sort_state == 2:
        query += " ORDER BY Users.fname DESC, Users.lname DESC"

    cursor.execute(query, tuple(params))
    users = cursor.fetchall()
    cursor.close()
    return users

def fetch_companies():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, name, color FROM Companies")
    companies = cursor.fetchall()
    cursor.close()
    return companies

def add_company(name, color):
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO Companies (name, color) VALUES (%s, %s)", (name, color))
    mydb.commit()
    cursor.close()

def update_company(company_id, name, color):
    cursor = mydb.cursor()
    cursor.execute("UPDATE Companies SET name = %s, color = %s WHERE id = %s", (name, color, company_id))
    cursor.execute("UPDATE Users SET color = %s WHERE company_id = %s", (color, company_id))
    mydb.commit()
    cursor.close()

def fetch_company_by_name(name):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, color FROM Companies WHERE name = %s", (name,))
    company = cursor.fetchone()
    cursor.close()
    return company

def delete_company(company_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Users WHERE company_id = %s", (company_id,))
    cursor.execute("DELETE FROM Companies WHERE id = %s", (company_id,))
    mydb.commit()
    cursor.close()

def fetch_user_details(user_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
    SELECT Users.id, Users.fname, Users.lname, Companies.name as company, Users.address, Users.city, Users.county, Users.color, Users.photo 
    FROM Users 
    JOIN Companies ON Users.company_id = Companies.id 
    WHERE Users.id = %s
    """, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def delete_user(user_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
    mydb.commit()
    cursor.close()
    
def update_user(user_id, fname, lname, company, address, city, county, color, photo):
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            UPDATE Users
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s, photo = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, photo_data, user_id))
    else:
        cursor.execute("""
            UPDATE Users
            SET fname = %s, lname = %s, company_id = %s, address = %s, city = %s, county = %s, color = %s
            WHERE id = %s
        """, (fname, lname, company_id, address, city, county, company_color, user_id))
    mydb.commit()
    cursor.close()

def add_user(fname, lname, company, address, city, county, color, photo):
    cursor = mydb.cursor()
    company_data = fetch_company_by_name(company)
    company_id = company_data['id']
    company_color = company_data['color']
    if photo:
        photo_data = photo.read()
        cursor.execute("""
            INSERT INTO Users (fname, lname, company_id, address, city, county, color, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color, photo_data))
    else:
        cursor.execute("""
            INSERT INTO Users (fname, lname, company_id, address, city, county, color)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (fname, lname, company_id, address, city, county, company_color))
    mydb.commit()
    cursor.close()