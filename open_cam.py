import cv2

#video_capture = cv2.VideoCapture(0)

video_capture = cv2.VideoCapture()
video_capture.open("http://10.66.66.3:8090/mjpeg")

anterior = 0

while True:
    if not video_capture.isOpened():
        print('Unable to load camera. Use the command "xhost +"')
        pass

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Display the resulting frame
    cv2.imshow('Video', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()