import base64
import cv2
import os
import decimal
from datetime import datetime
from datetime import date
from datetime import timedelta
from simple_facerec import SimpleFacerec
from face_db import FaceDB
from api import FaceApi
from dotenv import load_dotenv

def main():

    # Encode faces from a folder
    sfr = SimpleFacerec()
    fdb = FaceDB()
    fa = FaceApi()
    print("load Environment")
    load_dotenv()

    camera_url = os.getenv("CAMERA_URL")
    time_interval = int(os.getenv("INTERVAL"))
    tol = decimal.Decimal(os.getenv("TOL"))

    images_folder = 'face_database/'
    time_limit = timedelta(seconds=time_interval).total_seconds()

    fdb.get_encodings()

    last_encoding_date = fdb.last_encoding_date
    
    if last_encoding_date == None:
        last_encoding_date = date.today() - timedelta(days = 1)

    print("last_encoding_date is ", last_encoding_date)

    if last_encoding_date.date() < datetime.today():
        FaceDB.save_image_files() #last_encoding_date
        sfr.load_encoding_images("face_database/")    

    if len(sfr.known_face_encodings) > 0 : 
        fdb.insert_encodings(datetime.today(), sfr.known_face_encodings, sfr.known_face_names)

    # Load Camera
    #cap = cv2.VideoCapture(0)  
    print("Camera face detect starting")
    cap = cv2.VideoCapture()
    cap.open(camera_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set the desired width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set the desired height

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) # depends on fourcc available camera
    cap.set(cv2.CAP_PROP_FPS, 5)

    #Authorize to API
    fa.authorize()

    delay_time = 10
    last_time= datetime.now()
    try:

        while True:
            ret, frame = cap.read()
            
            # Perform face recognition
            print("While camera detecting...")
            face_locations, face_names = sfr.detect_known_faces_tol(frame, tolerance=tol)
            

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Draw a rectangle around the face
                #cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                
                #print("Convert to grayscale")
                # Convert the cropped image to grayscale
                crop_img = cv2.cvtColor(frame[top:bottom, left:right], cv2.COLOR_BGR2GRAY)

                if name == 'Unknown':
                    
                    folder_path = os.path.join(images_folder, name)

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    #current_time = datetime.now()
                    last_detection_time = datetime.fromtimestamp(os.path.getmtime(folder_path))
                    time_difference = (datetime.now() - last_detection_time).total_seconds()
                    
                    print(time_difference)
                    
                    # Check if the face has not been detected within the time limit
                    if time_difference >= time_limit:

                        print("Unknown image!")

                        # Save the image
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)

                        filename = os.path.join(folder_path, "Unknown.jpg")
                        
                        cv2.imwrite(filename, crop_img)
                        print(f"The saved face image is: {filename}")

                        with open(filename, 'rb') as img_file:
                                image_data = img_file.read()

                        # Encode the image data in base64
                        with open(filename, 'rb') as img_file:
                            fa.send_face_values_to_api_post([{"imageBase64": base64.b64encode(img_file.read()).decode('utf-8')}])
                            os.utime(folder_path)
                    
                # Check if the face is already known and detected
                elif name in face_names: 
                    folder_path = os.path.join(images_folder, name.split('_')[0])
                    filename = os.path.join(folder_path, f"{name}.jpg")

                    last_detection_time = datetime.fromtimestamp(os.path.getmtime(folder_path))
                    #time_difference = (current_time - last_detection_time).total_seconds()                    
                    time_difference = (datetime.now() - last_detection_time).total_seconds()
                    
                    print("We recognized: " + name)
                    
                    # Check if the face has not been detected within the time limit
                    if time_difference >= time_limit:
                                             

                        cv2.imwrite(filename, crop_img)
                        print(f"The saved face image is: {filename}")

                        # Read the image file as binary data
                        with open(filename, 'rb') as img_file:
                            image_data = img_file.read()

                        #print(name)
                        insert_id = name.split('_')[1]
 
                        # Send face values to Swagger UI API
                        # Encode the image data in base64
                        status_code = 111
                        with open(filename, 'rb') as img_file:
                            status_code = fa.send_face_values_to_api_put([{"pythonId": insert_id, "guid": name.split('_')[0]}])
                        
                        if status_code == 200:
                            fdb.insert_face_images(datetime.now(), name.split('_')[0], image_data) 
                            os.utime(folder_path)

                        
                        #last_time = datetime.now()
                        # Update the last detection time for the face
                        #known_faces[uuid.UUID(name).int] = current_time
                    else:
                        print("Time is not expired", time_difference)                    
            
            if len(face_names) == 0:           
                print("No face")

                # Generate timestamp in standard format
                


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

if __name__ == "__main__":
    main()
