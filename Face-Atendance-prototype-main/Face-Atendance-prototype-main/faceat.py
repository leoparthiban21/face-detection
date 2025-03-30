import cv2
import face_recognition
import os
import pandas as pd
import numpy as np
from datetime import datetime
import sys
def recognize_faces():
    path = 'student_images'
    images = []
    classNames = []
    mylist = os.listdir(path)

    # Load images and their names
    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    # Function to find face encodings
    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encoded_face = face_recognition.face_encodings(img)
            if encoded_face:
                encodeList.append(encoded_face[0])
        return encodeList

    # Encoding faces
    encoded_face_train = findEncodings(images)

    # Function to mark attendance in the CSV file
    def markAttendance(name, status):
        with open('Attendance.csv', 'r') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
        if name not in nameList:
            with open('Attendance.csv', 'a') as f:
                if len(myDataList) == 0:
                    f.writelines('Name,Time,Date,Status\n')
                now = datetime.now()
                time = now.strftime('%I:%M:%S:%p')
                date = now.strftime('%d-%B-%Y')
                f.writelines(f'\n{name}, {time}, {date}, {status}')
        user_df = pd.read_csv('users.csv')
        # Check if the name exists in the user.csv file
        if name in user_df['name'].values:
            # Update the Attendance Count column
            user_df.loc[user_df['name'] == name, 'attendance_count'] += 1
            # Save the updated user.csv file
            user_df.to_csv('users.csv', index=False)
    
    face_dict = {}
    for img, name in zip(images, classNames):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)
        if encoded_face:
            face_dict[tuple(encoded_face[0])] = name

    # Start capturing video for face recognition
    cap = cv2.VideoCapture(0)
    marked_names = []  # List to track which names have been marked

    while True:
        
        ret, img = cap.read()
        cv2.putText(img, "Press 'q' to close the window",(50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0, 0, 0), 2, cv2.LINE_AA)
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        faces_in_frame = face_recognition.face_locations(imgS)
        encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)

        for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
            matches = face_recognition.compare_faces(list(face_dict.keys()), encode_face)
            faceDist = face_recognition.face_distance(list(face_dict.keys()), encode_face)
            matchIndex = np.argmin(faceDist)

            if matches[matchIndex]:
                name = face_dict[list(face_dict.keys())[matchIndex]]
                if name in marked_names:
                    y1, x2, y2, x1 = faceloc
                    # Since we scaled down by 4 times, multiply back by 4
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, "Already Marked", (x1 + 6, y2 + 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                else:
                    now = datetime.now()
                    time = now.strftime('%H:%M')
                    if time < "08:30":
                        status = "Present"
                        color = (0, 255, 0)
                    else:
                        status = "Late"
                        color = (0, 0, 255)

                    y1, x2, y2, x1 = faceloc
                    # Since we scaled down by 4 times, multiply back by 4
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, status, (x1 + 6, y2 + 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                    marked_names.append(name)
                    markAttendance(name, status)
            else:
                y1, x2, y2, x1 = faceloc
                # Since we scaled down by 4 times, multiply back by 4
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(img, "You are not enrolled", (x1 + 10, y2 + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return "Attendance has been marked using face recognition."