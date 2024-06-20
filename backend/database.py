import mysql.connector
import os

_user="root"
_password="P@$$w0rd_"

def convert_to_binary_data(filename):
    with open(os.path.join(os.path.dirname(__file__), '..', 'static', 'images', filename), 'rb') as file:
        binary_data = file.read()
    return binary_data

mydb = mysql.connector.connect(
    host="localhost",
    user=_user,
    password=_password
)

cursor = mydb.cursor()

db_name = "mydb"
cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
database_exists = cursor.fetchone()

if not database_exists:
    cursor.execute(f"CREATE DATABASE {db_name}")
    print(f"Database '{db_name}' created successfully.")

cursor.close()
mydb.close()

mydb = mysql.connector.connect(
    host="localhost",
    user=_user,
    password=_password,
    database="mydb"
)

cursor = mydb.cursor()

cursor.execute("SHOW TABLES LIKE 'users'")
table_exists = cursor.fetchone()

if not table_exists:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fname VARCHAR(255),
        lname VARCHAR(255),
        company VARCHAR(255),
        address VARCHAR(255),
        city VARCHAR(255),
        county VARCHAR(255),
        color VARCHAR(255),
        photo BLOB
    );
    """

    cursor.execute(create_table_query)

    data_to_insert = [
        ('James', 'Butt', 'Benton', '6649 N Blue Gum St', 'New Orleans', 'Orleans', '#8bc447', convert_to_binary_data('james-butt.jpg')),
        ('Josephine', 'Darakjy', 'Chanay', '4 B Blue Ridge Blvd', 'Brighton', 'Livingston', '#8a3b93', None),
        ('Art', 'Venere', 'Chemel', '8 W Cerritos Ave', 'Bridgeport', 'Gloucester', '#1473bb', None),
        ('Lenna', 'Paprocki', 'Feltz Printing', '639 Main St', 'Anchorage', 'Anchorage', '#c32482', None),
        ('Donette', 'Foller', 'Feltz Printing', '34 Center St', 'Hamilton', 'Butler', '#c32482', None),
        ('Simona', 'Morasca', 'Chanay', '3 Mcauley Dr', 'Ashland', 'Ashland', '#8a3b93', None),
        ('Mitsue', 'Tollner', 'Benton', '7 Eads St', 'Chicago', 'Cook', '#8bc447', None),
        ('Leota', 'Dilliard', 'Commercial Press', '7 W Jackson Blvd', 'San Jose', 'Santa Clara', '#dde553', None),
        ('Sage', 'Wieser', 'Feltz Printing', '5 Boston Ave #88', 'Sioux Falls', 'Minnehaha', '#c32482', convert_to_binary_data('sage-weiser.jpg')),
        ('Kris', 'Marrier', 'Feltz Printing', '228 Runamuck Pl #2808', 'Baltimore', 'Baltimore', '#c32482', None),
        ('Minna', 'Amigon', 'Chanay', '2371 Jerrold Ave', 'Kulpsville', 'Montgomery', '#8a3b93', convert_to_binary_data('minna-amigon.jpg')),
        ('Abel', 'Maclead', 'Chemel', '37275 St Rt 17m M', 'Middle Island', 'Suffolk', '#1473bb', None),
        ('Kiley', 'Caldarera', 'Chemel', '25 E 75th St #69', 'Los Angeles', 'Los Angeles', '#1473bb', None),
        ('Bette', 'Ruta', 'Benton', '98 Connecticut Ave Nw', 'Chagrin Falls', 'Geauga', '#8bc447', None),
        ('Veronika', 'Albares', 'Benton', '56 E Morehead St', 'Laredo', 'Webb', '#8bc447', None)
    ]

    insert_query = """
    INSERT INTO Users (fname, lname, company, address, city, county, color, photo)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    for entry in data_to_insert:
        cursor.execute(insert_query, entry)

    mydb.commit()
cursor.close()