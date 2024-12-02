import tkinter as tk
from tkinter import Label, Frame

from tk_face_read import start_face_detection
from tk_qr_reder import start_qr_read
import threading

# Create the main window
root = tk.Tk()
root.title("UI Example")
root.geometry("1200x600")  # Adjust size as needed

# Calculate 60% width for video_frame and 40% for profile_frame
total_width = 1200
video_width = int(total_width * 0.6)  # 60% width for video_frame
profile_width = total_width - video_width  # Remaining 40% for profile_frame

# Video Streaming Section
video_frame = Frame(root, bd=2, relief="solid")
video_frame.place(x=10, y=10, width=video_width, height=580)

Label(video_frame, text="Video Streaming", font=("Arial", 14), anchor="w").pack(fill="x", pady=5, padx=5)
Label(video_frame, text="Date: 26/11/2024    Time: 13:25:00", anchor="w").pack(fill="x", pady=2, padx=5)

# Placeholder for video (use a label or canvas for actual video feed)
video_label = Label(video_frame, bg="lightgray", text="Video Stream Placeholder")
video_label.pack(expand=True, fill="both", padx=10, pady=10)

# Profile Matching Section
profile_frame = Frame(root, bd=2, relief="solid")
profile_frame.place(x=video_width + 20, y=10, width=profile_width, height=580)

Label(profile_frame, text="Profile Matching", font=("Arial", 14), anchor="w").pack(fill="x", pady=5, padx=5)

# Profile Matching Info
profile_info_frame = Frame(profile_frame)
profile_info_frame.pack(fill="x", pady=10, padx=5)

profile_pic_1 = Label(profile_info_frame, bg="lightgray", width=10, height=5, text="Face")
profile_pic_1.grid(row=0, column=0, padx=5)
profile_pic_2 = Label(profile_info_frame, bg="lightgray", width=10, height=5, text="Profile")
profile_pic_2.grid(row=0, column=1, padx=5)



# Gate Status Section
gate_status_label = Label(profile_frame, text="Gate Open", font=("Arial", 14), bg="green", fg="white", pady=5)
gate_status_label.pack(fill="x", pady=10)

gate_details_frame = Frame(profile_frame)
gate_details_frame.pack(fill="x", pady=5, padx=5)

Label(gate_details_frame, text="Et\tTime\tGate Pass\t%\tStatus", anchor="w").pack(fill="x")
Label(gate_details_frame, text="#01\t12:23:01\tGAT0021\t98\tGate Open", anchor="w").pack(fill="x", pady=5)




# Define threads to run each camera feed function concurrently
def start_qr_thread():
    start_qr_read(0, video_label)

def start_face_thread():
    start_face_detection(1)


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
