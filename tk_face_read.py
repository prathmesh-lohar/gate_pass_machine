import cv2
import os
from tkinter import Tk, Label
from PIL import Image, ImageTk
from simple_facerec import SimpleFacerec
from api_call import gate_pass_data  # assuming gate_pass_data is imported from your API
from datetime import datetime

from api_call import post_entry


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

def start_face_detection(cam_link, label: Label):
    """
    Start face detection and display video feed with detected face information.
    """
    cap = cv2.VideoCapture(cam_link)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def process_frame():
        global gate_open
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
                    date = datetime.now().strftime('%Y-%m-%d')   
                                                         
                    time_in = datetime.now().strftime('%H:%M:%S')
                    
                    data = {
                                "user": user_id,
                                "gatepass": "-",
                                "time_in": time_in,  # Date format: YYYY-MM-DD  # Time format: HH:MM:SS
                                "date": date ,
                                "image_type":"face",
                                "matching_percentage": face_percentage,   # Date format: YYYY-MM-DD
                                "activities":"Gate IN",
                                "alert":"-",
                                "action":"Open"
                            }
                    post_entry(data)
                                
                else:
                    gate_open = 0  # Keep the gate closed
                    print("Gate status: Closed")
                    
                    date = datetime.now().strftime('%Y-%m-%d')   
                                                         
                    time_in = datetime.now().strftime('%H:%M:%S')
                    
                    data = {
                                "user": "",
                                "gatepass": "-",
                                "time_in": time_in,  # Date format: YYYY-MM-DD  # Time format: HH:MM:SS
                                "date": date ,
                                "image_type":"face",
                                "matching_percentage": "00",   # Date format: YYYY-MM-DD
                                "activities":"Rejected",
                                "alert":"Unknown face",
                                "action":"Close"
                            }
                    post_entry(data)

            # Convert frame to Tkinter-compatible image format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)

        # Reduced frame update interval
        label.after(50, process_frame)

    process_frame()

# Example of starting face detection (this would be triggered in your main loop)
# def main():
#     root = Tk()
#     root.title("Face Detection System")
#     root.geometry("640x480")

#     # Create a label for the video feed
#     video_label = Label(root)
#     video_label.pack()

#     # Start face detection
#     start_face_detection(0, video_label)  # Pass 0 for the default webcam or a video file path

#     root.mainloop()

# if __name__ == "__main__":
#     main()
