import cv2
import face_recognition
import os
import pandas as pd
import numpy as np
from datetime import datetime

def clearAttendanceIfNewDay():
        current_date = datetime.now().strftime('%d-%m-%Y')
        last_attendance_date = None

        # Read the last entry in the attendance file to get the date
        if os.path.exists('Attendance.csv'):
            with open('Attendance.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Check if there are entries in the file
                    last_entry = lines[-1].strip()  # Get the last line and remove any extra whitespace
                    # Split the line into parts and check if it has at least 4 elements (Name, Time, Date, Status)
                    parts = last_entry.split(',')
                    if len(parts) >= 4:  # Ensure the line has enough elements
                        last_attendance_date = parts[2].strip()  # Date is the third element
        
        if last_attendance_date != current_date:
            with open('attendance.csv', 'w') as f:
                f.writelines('Name,Time,Date,Status\n')  # Only write header for the new day