from .database import mydb

def fetch_users(companies=None):
    cursor = mydb.cursor(dictionary=True)
    if companies:
        format_strings = ','.join(['%s'] * len(companies))
        cursor.execute("SELECT id, fname, lname, company, photo, color FROM Users WHERE company IN (%s)" % format_strings, tuple(companies))
    else:
        cursor.execute("SELECT id, fname, lname, company, photo, color FROM Users")
    users = cursor.fetchall()
    cursor.close()
    return users

def fetch_companies():
    cursor = mydb.cursor()
    cursor.execute("SELECT DISTINCT company FROM Users")
    companies = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return companies

def fetch_user_details(user_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT id, fname, lname, company, address, city, county, color, photo FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def delete_user(user_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
    mydb.commit()
    cursor.close()