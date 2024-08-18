import mysql.connector
import os
from werkzeug.security import generate_password_hash

_user = "root"
_password = "P@$$w0rd_"
db_name = "mydb"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user=_user,
        password=_password,
        database="mydb"
    )

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

cursor.execute(f"DROP DATABASE {db_name}") #Delete this after first run

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

cursor.execute("SHOW TABLES LIKE 'Employees'")
Employees_exists = cursor.fetchone()

cursor.execute("SHOW TABLES LIKE 'Companies'")
Companies_exists = cursor.fetchone()

cursor.execute("SHOW TABLES LIKE 'Users'")
Users_exists = cursor.fetchone()

if not Employees_exists or not Companies_exists or not Users_exists:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        color VARCHAR(255) UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fname VARCHAR(255),
        lname VARCHAR(255),
        company_id INT,
        address VARCHAR(255),
        city VARCHAR(255),
        county VARCHAR(255),
        color VARCHAR(255),
        photo BLOB,
        gps_location VARCHAR(255),
        date_account_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        salary DECIMAL(10, 2),
        date_of_birth DATE,
        job_title VARCHAR(255),
        employment_status ENUM('active', 'suspended'),
        isDeleted BOOLEAN DEFAULT FALSE,
        CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES Companies(id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)
    
    cursor.execute("""
    TRUNCATE TABLE Employees;
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

    employees = [
        ('James', 'Butt', company_dict['Benton'], 'Times Square', 'New York City', 'New York', '#8bc447', convert_to_binary_data('james-butt.jpg'), '40.7589, -73.9851', '2022-01-01', 55000.00, '1980-05-15', 'Software Engineer', 'active'),
        ('Josephine', 'Darakjy', company_dict['Chanay'], 'Golden Gate Bridge', 'San Francisco', 'California', '#8a3b93', None, '37.8003, -122.4804', '2022-02-10', 60000.00, '1985-06-20', 'Project Manager', 'active'),
        ('Art', 'Venere', company_dict['Chemel'], 'White House', 'Washington', 'Washington DC', '#1473bb', None, '38.8951, -77.0367', '2021-12-15', 47000.00, '1990-08-12', 'Designer', 'active'),
        ('Lenna', 'Paprocki', company_dict['Feltz Printing'], 'Grand Canyon National Park', 'Arizona', 'Arizona', '#c32482', None, '36.1069, -112.1129', '2021-11-10', 52000.00, '1983-04-05', 'Marketing Specialist', 'active'),
        ('Donette', 'Foller', company_dict['Feltz Printing'], 'Walt Disney World', 'Orlando', 'Florida', '#c32482', None, '28.3816, -81.5784', '2021-10-20', 48000.00, '1991-07-22', 'Sales Associate', 'suspended'),
        ('Simona', 'Morasca', company_dict['Chanay'], 'Empire State Building', 'New York City', 'New York', '#8a3b93', None, '40.7484, -73.9857', '2022-03-05', 45000.00, '1987-12-14', 'HR Manager', 'active'),
        ('Mitsue', 'Tollner', company_dict['Benton'], 'Yellowstone National Park', 'Wyoming', 'Wyoming', '#8bc447', None, '44.4392, -110.5908', '2022-04-25', 62000.00, '1978-01-30', 'Data Analyst', 'active'),
        ('Leota', 'Dilliard', company_dict['Commercial Press'], 'Yosemite National Park', 'California', 'California', '#dde553', None, '37.8615, -119.5675', '2022-05-15', 57000.00, '1982-06-17', 'Quality Assurance', 'suspended'),
        ('Sage', 'Wieser', company_dict['Feltz Printing'], 'Niagara Falls', 'New York', 'New York', '#c32482', convert_to_binary_data('sage-weiser.jpg'), '43.0845, -79.0754', '2021-06-12', 53000.00, '1989-09-23', 'IT Support', 'active'),
        ('Kris', 'Marrier', company_dict['Feltz Printing'], 'Mount Rushmore', 'Keystone', 'South Dakota', '#c32482', None, '43.8751, -103.4648', '2021-07-07', 49000.00, '1984-11-19', 'Operations Manager', 'active'),
        ('Minna', 'Amigon', company_dict['Chanay'], 'Lincoln Memorial', 'Washington', 'Washington DC', '#8a3b93', convert_to_binary_data('minna-amigon.jpg'), '38.8889, -77.0302', '2021-08-22', 61000.00, '1977-02-13', 'Finance Manager', 'active'),
        ('Abel', 'Maclead', company_dict['Chemel'], 'The Strip', 'Las Vegas', 'Nevada', '#1473bb', None, '36.1147, -115.1728', '2022-06-20', 58000.00, '1988-03-09', 'Consultant', 'active'),
        ('Kiley', 'Caldarera', company_dict['Chemel'], 'Alcatraz Island', 'San Francisco', 'California', '#1473bb', None, '37.8267, -122.4230', '2022-07-18', 60000.00, '1993-10-01', 'Product Manager', 'active'),
        ('Bette', 'Ruta', company_dict['Benton'], 'Willis Tower', 'Chicago', 'Illinois', '#8bc447', None, '41.8781, -87.6298', '2021-09-15', 55000.00, '1981-12-25', 'Administrator', 'suspended'),
        ('Veronika', 'Albares', company_dict['Benton'], 'The Alamo', 'San Antonio', 'Texas', '#8bc447', None, '29.4241, -98.4852', '2021-11-30', 54000.00, '1986-08-08', 'Developer', 'active')
    ]

    cursor.executemany("""
        INSERT IGNORE INTO Employees (fname, lname, company_id, address, city, county, color, photo, gps_location, date_account_created, salary, date_of_birth, job_title, employment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, employees)
    
    password = generate_password_hash("admin", method='pbkdf2:sha256')
    
    cursor.execute(f"""
    INSERT IGNORE INTO Users (username, email, password)
    VALUES ('admin', 'admin@example.com', '{password}')
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        start_date DATE,
        end_date DATE,
        budget DECIMAL(10, 2),
        time_estimation INT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ProjectCompanies (
        project_id INT,
        company_id INT,
        PRIMARY KEY (project_id, company_id),
        FOREIGN KEY (project_id) REFERENCES Projects(id),
        FOREIGN KEY (company_id) REFERENCES Companies(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ProjectEmployees (
        project_id INT,
        employee_id INT,
        PRIMARY KEY (project_id, employee_id),
        FOREIGN KEY (project_id) REFERENCES Projects(id),
        FOREIGN KEY (employee_id) REFERENCES Employees(id)
    );
    """)
    
    projects = [
        {
            "name": "Project Alpha",
            "description": "Developing a new AI model.",
            "start_date": "2023-01-10",
            "end_date": "2023-07-15",
            "budget": 150000,
            "time_estimation": 180,
            "company_ids": [1, 2],
            "employee_ids": [1, 2, 7]
        },
        {
            "name": "Project Beta",
            "description": "Upgrading the infrastructure.",
            "start_date": "2023-03-01",
            "end_date": "2023-10-01",
            "budget": 200000,
            "time_estimation": 214,
            "company_ids": [2, 3],
            "employee_ids": [6, 12]
        },
        {
            "name": "Project Gamma",
            "description": "Implementing cloud solutions.",
            "start_date": "2022-06-20",
            "end_date": "2023-02-20",
            "budget": 250000,
            "time_estimation": 245,
            "company_ids": [3, 4],
            "employee_ids": [3, 9]
        },
        {
            "name": "Project Delta",
            "description": "Redesigning the corporate website.",
            "start_date": "2023-05-10",
            "end_date": "2023-12-10",
            "budget": 90000,
            "time_estimation": 180,
            "company_ids": [1, 4],
            "employee_ids": [15, 10]
        },
        {
            "name": "Project Epsilon",
            "description": "Deploying a new CRM system.",
            "start_date": "2022-11-15",
            "end_date": "2023-04-20",
            "budget": 120000,
            "time_estimation": 157,
            "company_ids": [1, 2, 3],
            "employee_ids": [11, 13, 14]
        },
        {
            "name": "Project Zeta",
            "description": "Research and development for a new product.",
            "start_date": "2023-02-28",
            "end_date": "2023-11-30",
            "budget": 300000,
            "time_estimation": 275,
            "company_ids": [3],
            "employee_ids": [3]
        },
        {
            "name": "Project Eta",
            "description": "Expansion into new markets.",
            "start_date": "2023-08-01",
            "end_date": "2024-01-15",
            "budget": 175000,
            "time_estimation": 168,
            "company_ids": [2, 4],
            "employee_ids": [10, 11]
        },
        {
            "name": "Project Theta",
            "description": "Implementing data analytics platform.",
            "start_date": "2023-04-01",
            "end_date": "2023-12-01",
            "budget": 220000,
            "time_estimation": 245,
            "company_ids": [1, 3],
            "employee_ids": [1 ,12 ,13]
        }
    ]
    
    for project in projects:
        cursor.execute("""
        INSERT INTO Projects (name, description, start_date, end_date, budget, time_estimation)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (project["name"], project["description"], project["start_date"], project["end_date"], project["budget"], project["time_estimation"]))
        project_id = cursor.lastrowid

        for company_id in project["company_ids"]:
            cursor.execute("""
            INSERT INTO ProjectCompanies (project_id, company_id)
            VALUES (%s, %s)
            """, (project_id, company_id))
            
        for employee_id in project["employee_ids"]:
            cursor.execute("""
            INSERT INTO ProjectEmployees (project_id, employee_id)
            VALUES (%s, %s)
            """, (project_id, employee_id))
    
    mydb.commit()
    print("Successfully created tables")
    
else: print("Tables already exist")
    
cursor.close()
mydb.close()
