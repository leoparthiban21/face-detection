from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import csv
import os
from datetime import datetime
from faceat import recognize_faces

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Admin credentials
admin_credentials = {'admin@example.com': 'adminpassword'}

# Route: Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Route: Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in admin_credentials and admin_credentials[email] == password:
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin Credentials')
    return render_template('admin_login.html')

# Route: Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

    
# Route: Student Login
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with open('users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['email'] == email and row['password'] == password:
                    return render_template("student_details.html",res1=row['name'],res2=row['email'],res3=row['age'],res4=row['attendance_count'])
            flash('Invalid Student Credentials')
    return render_template('student_login.html')

# Route: Take Attendance
@app.route('/attendance')
def attendance():
    result = recognize_faces()
    return render_template('attendance.html', result=result)




@app.route('/today_details')
def today_details():    
    users = []
    try:
        with open('Attendance.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError:
        return "Error: users.csv not found.", 404
    
    # Render the data in an HTML template
    return render_template("today_details.html", Attendance=users)


@app.route("/user_details")
def user_detail():
    # Read the CSV file
    users = []
    try:
        with open('users.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError:
        return "Error: users.csv not found.", 404

    # Render the data in an HTML template
    return render_template("user_details.html", users=users)

def clearAttendanceIfNewDay():
    current_date = datetime.now().strftime('%d-%m-%Y')
    last_attendance_date = None

    # Read the last entry in the attendance file to get the date
    if os.path.exists('Attendance.csv'):
        with open('Attendance.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:  # Check if there are entries in the file
                last_entry = lines[-1].strip()  # Get the last line and remove any extra whitespace
                parts = last_entry.split(',')
                if len(parts) >= 4:
                    last_attendance_date = parts[2].strip()  # Date is the third element

    if last_attendance_date != current_date:
        with open('Attendance.csv', 'w') as f:  # Fixed the filename case
            f.writelines('Name,Time,Date,Status\n')  # Only write header for the new day
        return "Attendance cleared for the new day"
    return "No change in attendance, already up to date."

@app.route('/clear_details')
def clear_details():
    message = clearAttendanceIfNewDay()
    return render_template('clear_details.html', message=message)
    


if __name__ == '__main__':
    app.run(debug=True)