from flask import Flask, render_template, request, redirect, url_for, session, send_file
import mysql.connector
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'Guna@2604'  # Replace with a more secure key

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL user
    'password': 'Guna@2604',  # Replace with your MySQL password
    'database': 'employee_management'
}

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to calculate values
def calculate_values(brick):
    if brick > 90:
        round_bricks = brick + 10
    elif brick >= 50:
        round_bricks = brick + 10
    else:
        round_bricks = brick

    per_brick_amount = 5  # Default amount per brick
    total_amount = round_bricks * per_brick_amount

    return round_bricks, total_amount, per_brick_amount

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        if user[3] == 'owner':
            return redirect(url_for('owner_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    return "Invalid credentials, please try again."

@app.route('/owner_dashboard')
def owner_dashboard():
    if session.get('role') != 'owner':
        return "Access denied."
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template('owner_dashboard.html', employees=employees)

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = %s", (session['user_id'],))
    employees = cursor.fetchall()
    conn.close()
    return render_template('employee_dashboard.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if session.get('role') != 'owner':
        return "Access denied."
    name = request.form['name']
    line = int(request.form['line'])
    brick = int(request.form['brick'])
    
    date = datetime.now().strftime("%Y-%m-%d")
    day = datetime.now().strftime("%A")
    total_bricks = brick
    round_bricks, total_amount, per_brick_amount = calculate_values(brick)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (date, day, name, line, brick, total_bricks, round_bricks, per_brick_amount, total_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (date, day, name, line, brick, total_bricks, round_bricks, per_brick_amount, total_amount)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('owner_dashboard'))

@app.route('/export_excel')
def export_excel():
    if session.get('role') != 'owner':
        return "Access denied."
    conn = get_db_connection()
    query = "SELECT * FROM employees"
    employees = pd.read_sql(query, conn)
    conn.close()
    excel_path = "employee_data.xlsx"
    employees.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form action="{{ url_for('login_post') }}" method="POST">
        <label>Username:</label>
        <input type="text" name="username" required><br>
        <label>Password:</label>
        <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>



