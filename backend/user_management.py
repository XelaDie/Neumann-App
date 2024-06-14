from .database import mydb

def fetch_users():
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT id, fname, lname, company, photo, color FROM Users")
  users = cursor.fetchall()
  cursor.close()
  return users

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
    
