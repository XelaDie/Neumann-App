import re
import random
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, flash
from .database import get_connection

def send_confirmation_email(email, code, email_type='signup'):
    sender = 'neumannapp@outlook.com'
    receiver = email
    subject = 'Your Confirmation Code'
    if email_type == 'signup':
        body = f"""
        Dear User,

        Thank you for signing up. Your confirmation code is: {code}

        Please enter this code on the signup confirmation page to activate your account.

        Best regards,
        The Implify Team
        """
    elif email_type == 'reset':
        body = f"""
        Dear User,

        We received a request to reset your password. Your reset code is: {code}

        Please enter this code on the password reset page to reset your password.

        Best regards,
        The Implify Team
        """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()
        server.login(sender, 'nwtdjqwroqkrocpp')
        server.sendmail(sender, receiver, msg.as_string())

def signup_user(username, email, password):
    if len(username) < 3:
        flash('Username must be at least 3 characters long.', 'error')
        return False

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        flash('Invalid email address.', 'error')
        return False

    if not re.findall(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}', password):
        flash("Password doesn't match the requirments", 'error')
        return False

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    mydb = get_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT * FROM Users WHERE BINARY username= %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash('Username already exists.', 'error')
        return False

    cursor.execute("SELECT * FROM Users WHERE email= %s", (email,))
    existing_email = cursor.fetchone()
    if existing_email:
        flash('Email already exists.', 'error')
        return False

    confirmation_code = random.randint(100000, 999999)
    send_confirmation_email(email, confirmation_code, email_type='signup')
    session['confirmation_code'] = confirmation_code
    session['temp_user'] = {'username': username, 'email': email, 'password': hashed_password}
    
    mydb.commit()
    mydb.close()

    return True

def confirm_signup(code):
    if 'confirmation_code' in session and code == str(session['confirmation_code']):
        temp_user = session.pop('temp_user')
        mydb = get_connection()
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)", 
                       (temp_user['username'], temp_user['email'], temp_user['password']))
        mydb.commit()
        mydb.close()
        return True
    else:
        flash('Invalid confirmation code.', 'error')
        return False

def login_user(username, password):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Users WHERE BINARY username= %s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[3], password):
        session['username'] = user[1]
        return True
    else:
        flash('Invalid username or password.', "error")
        return False

def forgot_password(email):
    mydb = get_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Users WHERE email= %s", (email,))
    user = cursor.fetchone()
    mydb.close()
    if user:
        reset_code = random.randint(100000, 999999)
        send_confirmation_email(email, reset_code, email_type='reset')
        session['reset_code'] = reset_code
        session['reset_email'] = email
        return True
    else:
        flash('Email not found.', 'error')
        return False

def reset_password(code, new_password):
    if 'reset_code' in session and code == str(session['reset_code']):
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        email = session.pop('reset_email')
        mydb = get_connection()
        cursor = mydb.cursor()
        cursor.execute("UPDATE Users SET password= %s WHERE email= %s", (hashed_password, email))
        mydb.commit()
        mydb.close()
        return True
    else:
        flash('Invalid reset code.', 'error')
        return False

def logout_user():
    session.pop('username', None)
    return True