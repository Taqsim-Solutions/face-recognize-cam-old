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
    ftp_images = os.getenv("FTP_IMAGES")
    time_limit = timedelta(seconds=time_interval).total_seconds()

    fdb.get_encodings()

    last_encoding_date = fdb.last_encoding_date
    
    if last_encoding_date == None:
        last_encoding_date = date.today() - timedelta(days = 1)

    print("last_encoding_date is ", last_encoding_date)

    if last_encoding_date < date.today():
        FaceDB.save_image_files() #last_encoding_date
        sfr.load_encoding_images(images_folder)    

    if len(sfr.known_face_encodings) > 0 : 
        fdb.insert_encodings(datetime.today(), sfr.known_face_encodings, sfr.known_face_names)
    else:
        sfr.known_face_encodings = fdb.known_face_encodings
        sfr.known_face_names = fdb.known_face_names

    #Authorize to API
    fa.authorize()

    try:

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
                        img_date = filename.split("_")

                        year = img_date[2][:4]
                        month = img_date[2][4:6]
                        day =img_date[2][6:8]
                        hour =img_date[2][8:10]
                        minutes =img_date[2][10:12]
                        seconds =img_date[2][12:14]
                        milliseconds =img_date[2][14:17]
                        
                        last_detection_time = datetime.strptime(year + "-" + month + "-" + day+ " "+hour+ ":" +minutes+ ":" +seconds, '%Y-%m-%d %H:%M:%S')

                        comingTime = year + "-" + month + "-" + day+  "T"+hour+ ":" +minutes+ ":" +seconds+"."+milliseconds+"Z"

                        face_locations, face_names = sfr.image_detect_known_faces_tol(rgb_img, tolerance=tol)

                        for (top, right, bottom, left), name in zip(face_locations, face_names):
                        
                            if name == 'Unknown':
                                
                                time_difference = (datetime.now() - last_detection_time).total_seconds()
                                
                                print(time_difference)
                                
                                # Check if the face has not been detected within the time limit
                                #if time_difference >= time_limit:

                                print("Unknown image!")
                                
                                crop_img = cv2.cvtColor(rgb_img[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
                                cv2.imwrite(filename+".jpg", crop_img)
                                
                                # Encode the image data in base64
                                #2024-04-15T07:54:55.451Z
                                
                                with open(filename+".jpg", 'rb') as img_file:    
                                    fa.send_face_values_to_api_post([{"imageBase64": base64.b64encode(img_file.read()).decode('utf-8'), "comingTime": comingTime}])
                                    
                                os.remove(filename+".jpg")
                                    
                                #else:
                                #    break
                            # Check if the face is already known and detected
                            elif name in face_names: 

                                filename = images_folder + name.split('_')[0]+ "/" + name.split('_')[0] + ".jpg"

                                last_detection_time = datetime.now() - timedelta(days = 1)

                                if(os.path.isfile(filename)):
                                    last_detection_time = datetime.fromtimestamp(os.path.getmtime(filename))

                                crop_img = cv2.cvtColor(rgb_img[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
                                cv2.imwrite(filename, crop_img)

                                
                                time_difference = (datetime.now() - last_detection_time).total_seconds()
                                
                                print("We recognized: " + name)
                                
                                # Check if the face has not been detected within the time limit
                                if time_difference >= time_limit:                                                        
                                    
                                    #print(name)
                                    insert_id = name.split('_')[1]
                                                
                                    fa.send_face_values_to_api_put([{"pythonId": insert_id, "guid": name.split('_')[0], "comingTime": comingTime}])
                                    
                                    with open(filename, 'rb') as img_file:  
                                        fdb.insert_face_images(last_detection_time, name.split('_')[0], img_file.read()) 
                                    
                                else:
                                    print("Time is not expired", time_difference)  
                    
                        if len(face_names) == 0:           
                            print("No face")

                        if os.path.exists(img_path):
                            os.remove(img_path)
                            print(f"The file {img_path} has been deleted.")
                        else:
                            print(f"The file {img_path} does not exist.")

    except Exception as e:
        print(f"Error occurred : {str(e)}")

    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
