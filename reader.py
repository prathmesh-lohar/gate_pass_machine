import cv2
import json
import time

# Initialize the QRCode detector
qr_code_detector = cv2.QRCodeDetector()

# Variable to indicate gate status
gate_open = 0


def startqrread(cam):

    cap = cv2.VideoCapture(cam)

    while True:
        # Read the frame from the camera
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect and decode the QR code
        data, bbox, _ = qr_code_detector.detectAndDecode(frame)
        
        # If there is a QR code detected
        if bbox is not None:
            # Draw a bounding box around the QR code
            for i in range(len(bbox)):
                point1 = tuple(map(int, bbox[i][0]))
                point2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
                cv2.line(frame, point1, point2, (0, 255, 0), 2)
            
            # If the QR code has data, check the content
            if data:
                print("QR Code detected:", data)
                cv2.putText(frame, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                try:
                    # Parse the QR code data as JSON
                    qr_data = json.loads(data)
                    
                    # Check if "user" is 1 to trigger the gate open
                    if qr_data.get("user") == 1:
                        print("User verified, opening gate....,  Serial input: 1")
                        gate_open = 1
                        
                        # Wait for 2 seconds while the gate is open
                        time.sleep(5)
                        
                        # Close the gate
                        gate_open = 0
                        print("Gate closed. serial input: 0")
                except json.JSONDecodeError:
                    print("Invalid QR code data format.")

        # Display the result
        cv2.imshow("QR Code Reader", frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()
    

