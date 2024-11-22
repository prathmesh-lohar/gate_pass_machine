import cv2
import os
import time
from simple_facerec import SimpleFacerec

# Initialize face recognition
sfr = SimpleFacerec()
faces_directory = "faces/"
sfr.load_encoding_images(faces_directory)  # Initial loading of images

# Store the initially loaded images to detect any new images later
known_images = set(os.listdir(faces_directory))

def check_for_new_images():
    global known_images
    current_images = set(os.listdir(faces_directory))
    if current_images != known_images:
        sfr.load_encoding_images(faces_directory)  # Reload encodings
        known_images = current_images
        print("New images detected and loaded for encoding.")

def start_face_detection(cam_link, win_name):
    print(f"Starting face detection on camera -- {cam_link}")
    
    cap = cv2.VideoCapture(cam_link)

    while True:
        check_for_new_images()  # Check for new images each iteration

        ret, frame = cap.read()
        if not ret:
            break

        # Face Detection
        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        # Display the video feed with detected faces
        cv2.imshow(win_name, frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

# start_face_detection(1, "Face Detection")  # For webcam
