import mysql.connector
import os

_user = "root"
_password = "P@$$w0rd_"

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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        color VARCHAR(255) UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fname VARCHAR(255),
        lname VARCHAR(255),
        company_id INT,
        address VARCHAR(255),
        city VARCHAR(255),
        county VARCHAR(255),
        color VARCHAR(255),
        photo BLOB,
        CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES Companies(id)
    );
    """)

    companies = [
        ('Benton', '#8bc447'),
        ('Chanay', '#8a3b93'),
        ('Chemel', '#1473bb'),
        ('Feltz Printing', '#c32482'),
        ('Commercial Press', '#dde553')
    ]

    cursor.executemany("INSERT IGNORE INTO Companies (name, color) VALUES (%s, %s)", companies)
    mydb.commit()

    cursor.execute("SELECT id, name FROM Companies")
    company_dict = {name: company_id for company_id, name in cursor.fetchall()}

    users = [
        ('James', 'Butt', company_dict['Benton'], '6649 N Blue Gum St', 'New Orleans', 'Orleans', '#8bc447', convert_to_binary_data('james-butt.jpg')),
        ('Josephine', 'Darakjy', company_dict['Chanay'], '4 B Blue Ridge Blvd', 'Brighton', 'Livingston', '#8a3b93', None),
        ('Art', 'Venere', company_dict['Chemel'], '8 W Cerritos Ave', 'Bridgeport', 'Gloucester', '#1473bb', None),
        ('Lenna', 'Paprocki', company_dict['Feltz Printing'], '639 Main St', 'Anchorage', 'Anchorage', '#c32482', None),
        ('Donette', 'Foller', company_dict['Feltz Printing'], '34 Center St', 'Hamilton', 'Butler', '#c32482', None),
        ('Simona', 'Morasca', company_dict['Chanay'], '3 Mcauley Dr', 'Ashland', 'Ashland', '#8a3b93', None),
        ('Mitsue', 'Tollner', company_dict['Benton'], '7 Eads St', 'Chicago', 'Cook', '#8bc447', None),
        ('Leota', 'Dilliard', company_dict['Commercial Press'], '7 W Jackson Blvd', 'San Jose', 'Santa Clara', '#dde553', None),
        ('Sage', 'Wieser', company_dict['Feltz Printing'], '5 Boston Ave #88', 'Sioux Falls', 'Minnehaha', '#c32482', convert_to_binary_data('sage-weiser.jpg')),
        ('Kris', 'Marrier', company_dict['Feltz Printing'], '228 Runamuck Pl #2808', 'Baltimore', 'Baltimore', '#c32482', None),
        ('Minna', 'Amigon', company_dict['Chanay'], '2371 Jerrold Ave', 'Kulpsville', 'Montgomery', '#8a3b93', convert_to_binary_data('minna-amigon.jpg')),
        ('Abel', 'Maclead', company_dict['Chemel'], '37275 St Rt 17m M', 'Middle Island', 'Suffolk', '#1473bb', None),
        ('Kiley', 'Caldarera', company_dict['Chemel'], '25 E 75th St #69', 'Los Angeles', 'Los Angeles', '#1473bb', None),
        ('Bette', 'Ruta', company_dict['Benton'], '98 Connecticut Ave Nw', 'Chagrin Falls', 'Geauga', '#8bc447', None),
        ('Veronika', 'Albares', company_dict['Benton'], '56 E Morehead St', 'Laredo', 'Webb', '#8bc447', None)
    ]

    cursor.executemany("""
    INSERT INTO Users (fname, lname, company_id, address, city, county, color, photo)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, users)
    mydb.commit()

cursor.close()