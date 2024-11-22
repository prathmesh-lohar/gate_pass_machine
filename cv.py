import threading
import cv2
import json
import os
from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk
from simple_facerec import SimpleFacerec

# Initialize Tkinter window
window = Tk()
window.title("Face and QR Code Detection")
window.geometry("1200x600")

# Set up Frames and Labels for the two camera feeds
frame1 = Frame(window, width=600, height=600)
frame1.grid(row=0, column=0)
frame2 = Frame(window, width=600, height=600)
frame2.grid(row=0, column=1)

label_cam1 = Label(frame1)
label_cam1.pack()
label_cam2 = Label(frame2)
label_cam2.pack()

# Initialize face recognition and QR code detector
sfr = SimpleFacerec()
faces_directory = "faces/"
sfr.load_encoding_images(faces_directory)
qr_code_detector = cv2.QRCodeDetector()

# Load initially known images
known_images = set(os.listdir(faces_directory))

def check_for_new_images():
    """Reload encoding images if new images are added."""
    global known_images
    current_images = set(os.listdir(faces_directory))
    if current_images != known_images:
        sfr.load_encoding_images(faces_directory)
        known_images = current_images
        print("New images detected and loaded for encoding.")

# Function to process and display face detection in Tkinter
def update_face_detection():
    cap1 = cv2.VideoCapture(1)  # Set this to your actual camera index

    def process_frame():
        ret, frame = cap1.read()
        if ret:
            check_for_new_images()  # Reload images if any new images are added

            # Perform face detection
            face_locations, face_names = sfr.detect_known_faces(frame)
            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Convert to Tkinter-compatible format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label_cam1.imgtk = imgtk
            label_cam1.configure(image=imgtk)

        # Schedule the next frame update
        window.after(20, process_frame)  # Increase interval slightly

    process_frame()

# Function to process and display QR code detection in Tkinter
def update_qr_read():
    cap2 = cv2.VideoCapture(0)  # Set this to your actual camera index

    def process_frame():
        ret, frame = cap2.read()
        if ret:
            # Detect and decode the QR code
            data, bbox, _ = qr_code_detector.detectAndDecode(frame)

            if bbox is not None:
                # Draw bounding box and display QR code data
                for i in range(len(bbox)):
                    point1 = tuple(map(int, bbox[i][0]))
                    point2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
                    cv2.line(frame, point1, point2, (0, 255, 0), 2)
                
                if data:
                    try:
                        qr_data = json.loads(data)
                        if qr_data.get("user") == 1:
                            cv2.putText(frame, "Gate Open", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    except json.JSONDecodeError:
                        cv2.putText(frame, "Invalid QR Code", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Convert to Tkinter-compatible format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label_cam2.imgtk = imgtk
            label_cam2.configure(image=imgtk)

        # Schedule the next frame update
        window.after(20, process_frame)  # Increase interval slightly

    process_frame()

# Start both processes in separate threads
def start_threads():
    threading.Thread(target=update_face_detection, daemon=True).start()
    threading.Thread(target=update_qr_read, daemon=True).start()

# Function to release cameras on closing window
def on_close():
    cap1.release()
    cap2.release()
    window.destroy()

if __name__ == '__main__':
    # Start the threads and Tkinter main loop
    window.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close
    start_threads()
    window.mainloop()
