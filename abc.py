import cv2
import numpy as np
import time

# Initialize Haar Cascade classifiers for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Morse code dictionary
morse_code_dict = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', 
    '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', 
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', 
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', 
    '---..': '8', '----.': '9'
}

# Initialize variables for blink detection
blink_start_time = None
morse_code = ''
detected_code = ''

def detect_eyes(frame):
    """Detect eyes in the frame using Haar Cascade."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) == 0:
            return False
        return True
    return False

def interpret_blink(duration):
    """Interpret the blink duration into Morse code (dot or dash)."""
    if duration < 1.0:
        return '.'
    else:
        return '-'

def sender_loop():
    """Main loop for the sender side to capture blinks and send messages."""
    global blink_start_time, morse_code, detected_code

    # Start the webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect if eyes are open (for blink detection)
        eyes_open = detect_eyes(frame)

        if eyes_open and blink_start_time is not None:
            # Calculate the duration of the blink
            blink_duration = time.time() - blink_start_time
            morse_code += interpret_blink(blink_duration)  # Add blink to Morse code
            blink_start_time = None  # Reset blink start time after detecting the blink
        elif not eyes_open and blink_start_time is None:
            # Start tracking blink when eyes are closed
            blink_start_time = time.time()

        # Check if enough time has passed to consider the message complete
        if len(morse_code) > 0 and blink_start_time is not None and time.time() - blink_start_time > 1.5:
            detected_code += morse_code_dict.get(morse_code, '')
            morse_code = ''
            blink_start_time = None  # Reset after a full character

        # Write the decoded message to a file once completed
        if len(detected_code) > 0:
            with open('message.txt', 'w') as file:
                file.write(detected_code)  # Write the final decoded message
            print(f"Message sent: {detected_code}")
            detected_code = ''  # Reset after sending

        # Display the current Morse code and camera feed
        cv2.putText(frame, f'Morse Code: {detected_code}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Eye Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start the sender loop
if _name_ == "_main_":
    sender_loop()