from flask import Flask, Response
import threading


import cv2
import os
from tkinter import Tk, Label
from PIL import Image, ImageTk
from simple_facerec import SimpleFacerec
from api_call import gate_pass_data  # Assuming gate_pass_data is imported from your API
from datetime import datetime
import requests


# Initialize gate pass data
gate_pass_data = gate_pass_data()

# Initialize face recognition
sfr = SimpleFacerec()
faces_directory = "faces/"
sfr.load_encoding_images(faces_directory)
known_images = set(os.listdir(faces_directory))

gate_open = 0  # Initial state of the gate (closed)

def check_for_new_images():
    """
    Check if new images are added to the faces directory and reload encodings if necessary.
    """
    global known_images
    current_images = set(os.listdir(faces_directory))
    if current_images != known_images:
        sfr.load_encoding_images(faces_directory)
        known_images = current_images
        print("New images detected and loaded for encoding.")

def check_gate_pass(user_id):
    """
    Check if the user ID is in gate_pass_data and if their master admin approval is "pass".
    """
    global gate_pass_data
    for gatepass in gate_pass_data:
        if str(gatepass['user']) == user_id and gatepass['master_admin_approval'] == 'pass':
            return True
    return False

def save_face_image(image, file_path="temp_face.jpg"):
    """
    Save the detected face as a temporary image file.
    """
    cv2.imwrite(file_path, image)
    return file_path


def post_entry(data, image=None):
    """
    Post data to the API with the option to include an image file.
    """
    url = "http://localhost:8000/api/api/class-entries/"  # Replace with your API endpoint
    
    files = {}
    if image:
        with open(image, 'rb') as img_file:
            files['detected_face'] = ('face.jpg', img_file, 'image/jpeg')
            try:
                response = requests.post(url, data=data, files=files)
                print(f"Response: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error sending data to API: {e}")
    
    # Clean up the temporary file
    if image and os.path.exists(image):
        try:
            os.remove(image)
        except Exception as e:
            print(f"Error deleting file: {e}")



def handle_face_upload(face_image, user_id, face_percentage):
    """
    Handle API data preparation and file upload for a detected face.
    """
    date = datetime.now().strftime('%Y-%m-%d')
    time_in = datetime.now().strftime('%H:%M:%S')

    # Prepare data to send
    data = {
        "user": user_id,
        "gatepass": "-",
        "time_in": time_in,
        "date": date,
        "image_type": "face",
        "matching_percentage": face_percentage,
        "activities": "Gate IN",
        "alert": "-",
        "action": "Open",
    }

    # Save face image temporarily
    temp_file_path = save_face_image(face_image)

    # Post data with file
    post_entry(data, image=temp_file_path)



# Flask application
app = Flask(__name__)

# Shared variable for the HTTP video feed
global_frame = None

def generate_video_feed():
    """
    Generate a video stream for the HTTP feed.
    """
    global global_frame
    while True:
        if global_frame is not None:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', global_frame)
            if not ret:
                continue
            # Yield the frame as part of an HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """
    HTTP endpoint for the video feed.
    """
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    """
    Start the Flask application on a separate thread.
    """
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def start_face_detection(cam_link, label: Label):
    """
    Start face detection and display video feed with detected face information.
    """
    global global_frame
    cap = cv2.VideoCapture(cam_link)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def process_frame():
        global global_frame, gate_open
        ret, frame = cap.read()
        if ret:
            check_for_new_images()

            frame_height, frame_width = frame.shape[:2]
            frame_area = frame_width * frame_height

            # Detect faces less frequently for reduced lag
            face_locations, face_names = sfr.detect_known_faces(frame)
            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc
                face_area = (x2 - x1) * (y2 - y1)
                face_percentage = (face_area / frame_area) * 100

                # Draw rectangle around the face
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
                # Display name and percentage on the frame
                cv2.putText(
                    frame,
                    f"{name} ({face_percentage:.2f}%)",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1,
                    (0, 0, 200),
                    2
                )
                print(f"Face detected: {name}, {face_percentage:.2f}% of frame")
                string = name
                user_id = string.split('_')[0]  # Extract ID from the name string
                print("User ID:", user_id)

                # Check if the user has an approved gate pass
                if check_gate_pass(user_id):
                    gate_open = 1  # Open the gate
                    print("Gate status: Open")
                    
                    # Crop the face region from the frame
                    face_image = frame[y1:y2, x1:x2]

                    # Handle API upload
                    handle_face_upload(face_image, user_id, face_percentage)
                else:
                    gate_open = 0  # Keep the gate closed
                    print("Gate status: Closed")
                    
                    # Prepare data for unknown faces
                    date = datetime.now().strftime('%Y-%m-%d')   
                    time_in = datetime.now().strftime('%H:%M:%S')
                    data = {
                        "user": "",
                        "gatepass": "-",
                        "time_in": time_in,
                        "date": date,
                        "image_type": "face",
                        "matching_percentage": "0",
                        "activities": "Rejected",
                        "alert": "Unknown face",
                        "action": "Close",
                    }

                    # Post data without file
                    post_entry(data)

            # Update the global frame for HTTP streaming
            global_frame = frame.copy()

            # Convert frame to Tkinter-compatible image format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)

        # Reduced frame update interval
        label.after(50, process_frame)

    process_frame()

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()
