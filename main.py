import tkinter as tk
from tkinter import LabelFrame
from tk_face_read import start_face_detection
from tk_qr_reder import start_qr_read
import threading
import requests

# Initialize main application window
root = tk.Tk()
root.title("Smart Gate Pass")
root.geometry("800x400")  # Set the window size as needed

# Create a frame for Cam1
cam1_frame = LabelFrame(root, text="Qr Code Detection", padx=10, pady=10)
cam1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create a frame for Cam2
cam2_frame = LabelFrame(root, text="Face Detection", padx=10, pady=10)
cam2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Configure the grid to make both columns expandable
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Placeholder labels for camera feed (can be replaced with actual video feed)
cam1_label = tk.Label(cam1_frame, text="Face Detection")
cam1_label.pack(expand=True, fill="both")

cam2_label = tk.Label(cam2_frame, text="Qr Code Detection")
cam2_label.pack(expand=True, fill="both")



# Define threads to run each camera feed function concurrently
def start_qr_thread():
    start_qr_read(1, cam1_label)

def start_face_thread():
    start_face_detection(0, cam2_label)


# Create and start threads
qr_thread = threading.Thread(target=start_qr_thread)
face_thread = threading.Thread(target=start_face_thread)


# Daemon threads ensure that they close when the main program exits
qr_thread.daemon = True
face_thread.daemon = True

qr_thread.start()
face_thread.start()


# Run the main loop
root.mainloop()
