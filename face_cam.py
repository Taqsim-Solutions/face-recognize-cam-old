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
import glob

def main():

    # Encode faces from a folder
    sfr = SimpleFacerec()
    fdb = FaceDB()
    fa = FaceApi()
    print("load Environment")
    load_dotenv()

    time_interval = int(os.getenv("INTERVAL"))
    tol = decimal.Decimal(os.getenv("TOL"))

    images_folder = 'face_database/'
    ftp_images = 'ftp/'
    time_limit = timedelta(seconds=time_interval).total_seconds()

    fdb.get_encodings()

    last_encoding_date = fdb.last_encoding_date
    
    if last_encoding_date == None:
        last_encoding_date = date.today() - timedelta(days = 1)

    print("last_encoding_date is ", last_encoding_date)

    if last_encoding_date < date.today():
        FaceDB.save_image_files() #last_encoding_date
        sfr.svc_load_encoding_images("face_database/")    

    if len(sfr.known_face_encodings) > 0 : 
        fdb.insert_encodings(datetime.today(), sfr.known_face_encodings, sfr.known_face_names)

    #Authorize to API
    fa.authorize()

    delay_time = 10
    try:


        #TODO 
        # 1.Load Images from FTP folder

        for root, dirs, files in os.walk(ftp_images):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                images = glob.glob(os.path.join(dir_path, "*.jpg"))

                if len(images) > 0:
                    print("{} encoding images found in '{}'.".format(len(images), dir_name))

                    for img_path in images:
                        img = cv2.imread(img_path)
                        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                        # Get the filename only from the initial file path.
                        basename = os.path.basename(img_path)
                        (filename, ext) = os.path.splitext(basename)
                        img_date = datetime.fromtimestamp(os.path.getmtime(img_path))

                        face_locations, face_names = sfr.image_detect_known_faces_tol(rgb_img, tolerance=tol)

                        for (top, right, bottom, left), name in zip(face_locations, face_names):
                        
                            if name == 'Unknown':
                                
                                time_difference = (datetime.now() - img_date).total_seconds()
                                
                                print(time_difference)
                                
                                # Check if the face has not been detected within the time limit
                                if time_difference >= time_limit:

                                    print("Unknown image!")

                                    # Save the image
                                    if not os.path.exists(folder_path):
                                        os.makedirs(folder_path)

                                    filename = os.path.join(folder_path, "Unknown.jpg")
                                    
                                    cv2.imwrite(filename, rgb_img)
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
                                        fdb.insert_face_images(img_date, name.split('_')[0], image_data) 
                                        os.utime(folder_path)

                                    
                                else:
                                    print("Time is not expired", time_difference)                    
                    
                        if len(face_names) == 0:           
                            print("No face")
    

        # 5.Remove Image from FTP folder

                


            # Display the resulting frame
            #cv2.imshow("Frame", frame)

            key = cv2.waitKey(delay_time)
            if key == 27:
                break

    except Exception as e:
        print(f"Error occurred : {str(e)}")

    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
