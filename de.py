import face_recognition
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, render_template, redirect, url_for, session

# Load known face encodings and names
known_face_encodings = []
known_face_names = []

# Load dataset images (Replace 'dataset' with actual image files)
dataset = {
    "person1": "dataset/person1.jpg",
    # "person2": "dataset/person2.jpg"
}

for name, img_path in dataset.items():
    image = face_recognition.load_image_file(img_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_names.append(name)

# Function to send email alert
def send_email_alert(intruder_image):
    sender_email = "kuralanbu25@gmail.com"
    receiver_email = "jdnarmatha0026@gmail.com"
    password = "fndw vfdu fkjc ljux"

    subject = "ALERT: Unauthorized Person Detected!"
    body = "An unknown person tried to access the system."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Alert Email Sent Successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Flask setup for login
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Hardcoded user login data (can be replaced with a database)
users = {
    "user": "pass",
    "username2": "password2"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["logged_in"] = True
            return redirect(url_for("face_recognition"))
        else:
            return "Invalid credentials, please try again."

    return render_template("login.html")

@app.route("/face_recognition")
def face_recognition():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # Initialize webcam and detect faces
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        # Convert the frame from BGR (OpenCV format) to RGB (face_recognition format)
        rgb_frame = frame[:, :, ::-1]

        # Detect faces in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Processing each face
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            # Find the best match for face
            best_match_index = np.argmin(face_distances) if matches else None

            if best_match_index is not None and matches[best_match_index]:
                name = known_face_names[best_match_index]
                print(f"Match Found: {name}")
            else:
                print("No match found")

        # Display the result on a window
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return "Session Ended"

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)

