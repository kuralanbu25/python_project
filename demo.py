from flask import Flask, render_template, request
import cv2
import face_recognition
import numpy as np
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# User credentials
USERNAME = "user"
PASSWORD = "pass"

# Email Configuration
SENDER_EMAIL = 'kuralanbu25@gmail.com'
SENDER_PASSWORD = 'fndw vfdu fkjc ljux'
RECIPIENT_EMAIL = 'jdbala0001@gmail.com'

# Path where authorized images are stored
AUTHORIZED_FACE_DIR = "authorized_faces"

# Load authorized face encodings
def load_authorized_faces():
    authorized_faces = []
    authorized_names = []

    for filename in os.listdir(AUTHORIZED_FACE_DIR):
        img_path = os.path.join(AUTHORIZED_FACE_DIR, filename)
        img = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(img)

        if len(encoding) > 0:
            authorized_faces.append(encoding[0])
            authorized_names.append(os.path.splitext(filename)[0])  # Get name without extension

    return authorized_faces, authorized_names

authorized_face_encodings, authorized_face_names = load_authorized_faces()

# Function to send an email alert
def send_email_alert():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = "Unauthorized Access Attempt"
        msg.attach(MIMEText("An unknown person tried to access the system!", 'plain'))

        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to recognize a face
def recognize_face():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot access the webcam.")
        return False

    print("Looking for a face...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not capture frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(authorized_face_encodings, face_encoding, tolerance=0.5)

            if True in matches:
                matched_idx = matches.index(True)
                name = authorized_face_names[matched_idx]
                print(f"Access Granted: {name}")
                cap.release()
                cv2.destroyAllWindows()
                return True  # Recognized face
            else:
                print("Unauthorized face detected. Sending alert email...")
                send_email_alert()
                cap.release()
                cv2.destroyAllWindows()
                return False  # Unrecognized face

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == USERNAME and password == PASSWORD:
        if recognize_face():
            return "Transaction Approved! Facial recognition passed."
        else:
            return "Transaction Failed! Unauthorized face detected."
    else:
        return "Invalid credentials!"

if __name__ == '__main__':
    app.run(debug=True)
