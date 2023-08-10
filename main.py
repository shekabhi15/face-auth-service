import os
import uuid
import face_recognition
from flask import Flask, render_template, request, redirect, send_from_directory, url_for

app = Flask(__name__)

# Folder to store user images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Dummy data for demo purposes
users = []

# Homepage
@app.route('/')
def index():
    message = ''
    return render_template('index.html', error=message)

# Register page
@app.route('/register')
def register():
    message = ''
    return render_template('register.html', error=message,  users=users)

# Register form submission
@app.route('/register', methods=['POST'])
def register_submit():
    username = request.form['username']
    image_file = request.files['fileInput']

    # Save uploaded image file to uploads folder
    unique_filename = str(uuid.uuid4()) + '.png'
    image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    image_file.save(image_path)

    # Add user to list
    users.append({'username': username, 'image_path': image_path, 'image_name': unique_filename})

    # Successful registration
    message = 'Registration successful. Please log in.'
    return render_template('register.html', error=message, users=users)

# Login form submission
@app.route('/login', methods=['POST'])
def login():
    print(users)
    # Get form data
    image_file = request.files['fileInput']

    # Authenticate user using face recognition
    for user in users:
        try:
            known_image = face_recognition.load_image_file(user['image_path'])
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_image = face_recognition.load_image_file(image_file)
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            face_distances = face_recognition.face_distance([known_encoding], unknown_encoding)
            print(face_distances)

        except:
            print("cannot find face")
            message = 'We were unable to find any faces based on the uploaded image. Please try again.'
            return render_template('index.html', error=message)

        if face_distances[0] < 0.5:
            
            # Successful login
            return redirect(url_for('dashboard'))

    # Failed login
    message = 'We were unable to verify your identity based on the uploaded image. Please try again.'
    return render_template('index.html', error=message)

# Dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route for serving uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
