import cv2
import numpy as np
import dlib
from imutils import face_utils
import pygame

pygame.init()

alarm_sound = pygame.mixer.Sound("music.wav")

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

sleep_threshold = 30 
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

face_frame = None 

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2
    elif 0.21 < ratio <= 0.25:
        return 1
    else:
        return 0

def eye_aspect_ratio(eye):
    A = compute(eye[1], eye[5])
    B = compute(eye[2], eye[4])
    C = compute(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    
    
    face_frame = frame.copy()

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        ear = (left_ear + right_ear) / 2.0

        left_blink = blinked(landmarks[36], landmarks[37],
                              landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43],
                               landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        if left_blink == 0 or right_blink == 0:
            drowsy += 1
            active = 0
            if drowsy >= sleep_threshold:
                status = "SLEEPING !!!"
                color = (255, 0, 0)
                alarm_sound.play()

        elif left_blink == 1 or right_blink == 1:
            drowsy = 0
            active = 0
            status = "Drowsy !"
            color = (0, 0, 255)

        else:
            drowsy = 0
            active += 1
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)
                alarm_sound.stop()

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    cv2.imshow("Frame", frame)
    cv2.imshow("Result of detector", face_frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
