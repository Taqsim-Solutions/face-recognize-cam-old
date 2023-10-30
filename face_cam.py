import base64
import cv2
import os
from datetime import datetime, timedelta
from simple_facerec import SimpleFacerec
from face_db import FaceDB
from api import FaceApi
import uuid
from dotenv import load_dotenv
import time

# Encode faces from a folder
sfr = SimpleFacerec()
fdb = FaceDB()
fa = FaceApi()

load_dotenv()

camera_url = os.getenv("CAMERA_URL")
database_host = os.getenv("DATABASE_HOST")
database_name = os.getenv("DATABASE_NAME")
#time_interval = os.getenv("INTERVAL")
#tol = os.getenv("TOL")

print("1")

images_folder = 'face_database/'
time_limit = timedelta(seconds=10).total_seconds()

fdb.get_encodings()

last_encoding_date = fdb.last_encoding_date



if last_encoding_date.date() <= datetime.today().date() :
    
    FaceDB.save_image_files()
    sfr.load_encoding_images("face_database/")    

    if len(sfr.known_face_encodings) > 0 : 
        fdb.insert_encodings(datetime.today(), sfr.known_face_encodings, sfr.known_face_names)

else:
    print("3.2")
    sfr.known_face_encodings = fdb.known_face_encodings
    sfr.known_face_names = fdb.known_face_names


# Load Camera
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture()
cap.open(camera_url)
print("6")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the desired width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the desired height

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # depends on fourcc available camera
cap.set(cv2.CAP_PROP_FPS, 10)

# Dictionary to store the names and last detection times of already detected faces
known_faces = sfr.known_face_names #dict(enumerate())

#Authorize to API
fa.authorize()

delay_time = 10

try:

    while True:
        ret, frame = cap.read()
        
        # Perform face recognition
        print(2.1)
        face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=0.55)
        
        current_time = datetime.now()

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            print(2.3)
            # Draw a rectangle around the face
            #cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Convert the cropped image to grayscale
            crop_img_gray = cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2GRAY)

            if name == 'Unknown':
                name = str(uuid.uuid1())
                folder_path = os.path.join(images_folder, name[len(name)-12:len(name)])
            
            #cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            #print(datetime.fromtimestamp(os.path.getmtime(os.path.join(images_folder, name))))
            #print((datetime(1582, 10, 15) + timedelta(microseconds=uuid.UUID(name).time//10)) + timedelta(hours=5))

            # Check if the face is already known and detected
            if name in face_names: 
                last_detection_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(images_folder, name)))
                time_difference = (current_time - last_detection_time).total_seconds()

                print(current_time)
                print(last_detection_time)
                print(time_difference)


                print("We recognized")
                # Check if the face has not been detected within the time limit
                if time_difference >= time_limit:
                    folder_path = os.path.join(images_folder, name[len(name)-12:len(name)])

                    # Generate timestamp in standard format
                    timestamp_for = timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    timestamp_for = timestamp_for.replace(":","_").replace(" ","_").replace("-","_")
                    filename = os.path.join(folder_path, f"{name}-{timestamp_for}.jpg")

                    # Save the grayscale image
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    cv2.imwrite(filename, crop_img_gray)
                    print(f"Saved updated face image to: {filename}")

                    # Send face values to Swagger UI API
                    # Encode the image data in base64
                    with open(filename, 'rb') as img_file:
                        fa.send_face_values_to_api([{"guid": name, "imageBase64": base64.b64encode(img_file.read()).decode('utf-8')}])


                    # Read the image file as binary data
                    with open(filename, 'rb') as img_file:
                        image_data = img_file.read()
                    
                    # Update the last detection time for the face
                    #known_faces[uuid.UUID(name).int] = current_time

                    fdb.insert_face_images(timestamp, name, image_data)  
            else:
                
                print("Not recognized")
                # Generate timestamp in standard format
                timestamp_for = timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                timestamp_for = timestamp_for.replace(":","_").replace(" ","_").replace("-","_")
                filename = os.path.join(folder_path, f"{name}-{timestamp_for}.jpg")


                # Save the grayscale image
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                cv2.imwrite(filename, crop_img_gray)
                print(f"Saved new grayscale face image to: {filename}")
                # Send face values to Swagger UI API

                # Encode the image data in base64
                with open(filename, 'rb') as img_file:
                    fa.send_face_values_to_api([{"guid": name, "imageBase64": base64.b64encode(img_file.read()).decode('utf-8')}])

                # Read the grayscale image file as binary data
                with open(filename, 'rb') as img_file:
                    image_data = img_file.read()

                fdb.insert_face_images(timestamp, name, image_data)    

        
        if len(face_names) == 0:           
            # name = str(uuid.uuid1())
            # folder_path = os.path.join(images_folder, name[len(name)-12:len(name)])
            print("No face")

            # Generate timestamp in standard format
            # timestamp_for = timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            # timestamp_for = timestamp_for.replace(":","_").replace(" ","_").replace("-","_")
            # filename = os.path.join(folder_path, f"{name}-{timestamp_for}.jpg")


            # # Save the grayscale image
            # if not os.path.exists(folder_path):
            #     os.makedirs(folder_path)
            # crop_img_gray = cv2.cvtColor(frame[face_locations[0][2]:face_locations[0][3], face_locations[0][0]:face_locations[0][1]], cv2.COLOR_BGR2GRAY) 

            # cv2.imwrite(filename, crop_img_gray)
            # print(f"Saved new grayscale face image to: {filename}")



        # Display the resulting frame
        #cv2.imshow("Frame", frame)

        key = cv2.waitKey(delay_time)
        if key == 27:
            break

except Exception as e:
    print(f"Error occurred : {str(e)}")

finally:
    cap.release()
    cv2.destroyAllWindows()

