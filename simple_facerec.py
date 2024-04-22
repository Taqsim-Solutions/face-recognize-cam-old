import face_recognition
import cv2
from sklearn import svm
import os
import datetime
import glob
import numpy as np

class SimpleFacerec:
    def __init__(self):
        self.encoding_image_paths = None
        self.encodings = None
        self.known_face_encodings = []
        self.known_face_names = []

        # Resize frame for a faster speed
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path: Path to the structured folder of images
        :return: List of face encodings and corresponding names
        """
        # Traverse the directory structure
        for root, dirs, files in os.walk(images_path):
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

                        # Get encoding
                        #face_encodings = face_recognition.face_encodings(rgb_img)
                        
                        face_locations = face_recognition.face_locations(rgb_img, number_of_times_to_upsample=2, model="hog")
                        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

                        if len(face_encodings) > 0:
                            img_encoding = face_encodings[0]

                            # Store file name and file encoding
                            self.known_face_encodings.append(img_encoding)
                            self.known_face_names.append(filename)


    def svc_load_encoding_images(self, images_path):
        for root, dirs, files in os.walk(images_path):    
            for person in dirs:
                pix = os.listdir(images_path + "/" + person)
                # Loop through each training image for the current person
                for person_img in pix:
                    # Get the face encodings for the face in each image file
                    face = face_recognition.load_image_file(images_path + "/" + person + "/" + person_img)
                    face_bounding_boxes = face_recognition.face_locations(face)

                    #If training image contains exactly one face
                    if len(face_bounding_boxes) == 1:
                        face_enc = face_recognition.face_encodings(face)[0]
                        # Add face encoding for current image with corresponding label (name) to the training data
                        self.known_face_encodings.append(face_enc)
                        self.known_face_names.append(person)
                    else:
                        print(person + "/" + person_img + " was skipped and can't be used for training")
        


    def detect_known_faces(self, frame: object) -> object:
        """

        :rtype: object
        """
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names

    def detect_known_faces_tol(self, frame, tolerance):
        #if frame is not None:

        #img = cv2.imread(imagePath)  from file
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        #else:
        #    self.frame_resizing = 0.25
        #    print("det",2)

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=2, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        print("detect_known_faces_tol")        
        
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=tolerance)
            
            #if True in matches:
            #    first_match_index = matches.index(True)
            #    name = self.known_face_names[first_match_index]
            #    print("first_match_index", first_match_index)
            #    print("name: ", name)
            #    face_names.append(name)

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            #print(face_encoding, face_distances, "23")
            
            if np.size(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                print("best_match_index ", best_match_index)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    face_names.append(name)                
                    print("name  ", name)
                else:
                    face_names.append("Unknown")

        #print(face_locations, "24")
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names

    def svc_detect_faces_tol(self, frame, tolerance):

        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        #else:
        #    self.frame_resizing = 0.25
        #    print("det",2)

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)        

        # Create and train the SVC classifier
        clf = svm.SVC(gamma='scale')
        clf.fit(self.known_face_encodings,self.known_face_names)   
        
        face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=1, model="hog")
        #face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        no = len(face_locations)
        print("Number of faces detected: ", no)
        
        face_names = []

        # Predict all the faces in the image using the trained classifier
        print("Found:")
        for i in range(no):
            test_image_enc = face_recognition.face_encodings(rgb_small_frame)[i]
            name = clf.predict([test_image_enc])
            print(*name)
            face_names.append(name)
        
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names


    @staticmethod
    def save_cropped_face(frame, face_coordinates, name, images_folder):
        top, bottom, left, right = face_coordinates

        folder_path = os.path.join(images_folder, name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = os.path.join(folder_path, f"{name}-{timestamp}.jpg")

        crop_img = frame[top:bottom, left:right]  # Color image
        crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)  # Convert to grayscale

        cv2.imwrite(filename, crop_img_gray)  # Save the grayscale image
        print(f"Saved cropped face to: {filename}")

    def compare_faces(self, encodings, face_encoding):
        pass

    def encode_face(self, param):
        pass


    def image_detect_known_faces_tol(self, rgb_small_frame, tolerance):
        
        face_locations = face_recognition.face_locations(rgb_small_frame, number_of_times_to_upsample=1, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        print("image_detect_known_faces_tol")        
        
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=tolerance)
            
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            #print(face_encoding, face_distances, "23")
            
            if np.size(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                print("best_match_index ", best_match_index)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    face_names.append(name)                
                    print("name  ", name)
                else:
                    face_names.append("Unknown")
                
            else:
                face_names.append("Unknown")

        #print(face_locations, "24")
        
        return face_locations, face_names