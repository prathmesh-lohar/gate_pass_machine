import cv2
import tkinter as tk
from tkinter import LabelFrame
from PIL import Image, ImageTk
import threading

# Initialize main application window
root = tk.Tk()
root.title("Smart Gate Pass")
root.geometry("800x400")  # Set the window size as needed

# Create a frame for Cam1 (QR Code Detection)
cam1_frame = LabelFrame(root, text="QR Code Detection", padx=10, pady=10)
cam1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create a frame for Cam2 (Face Detection)
cam2_frame = LabelFrame(root, text="Face Detection", padx=10, pady=10)
cam2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Configure the grid to make both columns expandable
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Placeholder labels for camera feed (can be replaced with actual video feed)
cam1_label = tk.Label(cam1_frame, text="QR Code Detection")
cam1_label.pack(expand=True, fill="both")

cam2_label = tk.Label(cam2_frame, text="Face Detection")
cam2_label.pack(expand=True, fill="both")

# Function to update the label with new frames
def update_label(label, img_tk):
    label.img_tk = img_tk
    label.config(image=img_tk)

# Function to handle MJPEG stream for QR code detection
def start_qr_read(cam_url, label):
    cap = cv2.VideoCapture(cam_url)  # Open MJPEG stream via URL or IP camera
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert the frame to RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        # Update the Tkinter label with the new frame
        label.after(0, update_label, label, img_tk)
    
    cap.release()

# Function to handle MJPEG stream for face detection
def start_face_detection(cam_url, label):
    cap = cv2.VideoCapture(cam_url)  # Open MJPEG stream via URL or IP camera
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert the frame to RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        # Update the Tkinter label with the new frame
        label.after(0, update_label, label, img_tk)
    
    cap.release()

# URLs for MJPEG streams (replace with actual MJPEG stream URLs or camera IPs)
qr_cam_url = 'http://192.168.1.101:8080/video'  # Example MJPEG stream URL for QR Code camera
face_cam_url = 'http://192.168.1.102:8080/video'  # Example MJPEG stream URL for Face Detection camera

# Create and start threads to run MJPEG feed functions concurrently
qr_thread = threading.Thread(target=start_qr_read, args=(qr_cam_url, cam1_label))
face_thread = threading.Thread(target=start_face_detection, args=(face_cam_url, cam2_label))

# Daemon threads ensure that they close when the main program exits
qr_thread.daemon = True
face_thread.daemon = True

qr_thread.start()
face_thread.start()

# Run the main loop
root.mainloop()
