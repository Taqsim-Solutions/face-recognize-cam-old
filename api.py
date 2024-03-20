import requests
import json
import sys
import os

class FaceApi:

    # Function to send face values to Swagger API
    def send_face_values_to_api(self, face_values):
        print("send_face_values_to_api")
        api_url = "https://face.taqsim.uz/api/face-recognitons"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }

        for face_value in face_values:
            response = requests.post(api_url, json=face_value, headers=headers, verify=True)

            print("Request Body:", json.dumps(face_value, indent=2))  # Print the request body
            print("Status Code:", response.status_code)  # Print the status code

            try:
                response_json = response.json()
                #print("Response Body:", json.dumps(response_json, indent=2))  # Print the response body
            except json.JSONDecodeError:
                print("Failed to decode response JSON.")

            if response.status_code == 200:
                print("Face values sent successfully to the API.")
            else:
                print(f"Failed to send face values to the API. Status code: {response.status_code}")

 
    def authorize(self):
        #Authorization
        api_url = 'https://face.taqsim.uz/api/authentication'
        myobj = {
            "login": "admin",
            "password": "123admin321"
        }

        response = requests.post(api_url, json = myobj)

        if response.status_code == 200:
            print("Authorized Successfully.")
        else:
            print(f"Failed to Authorize. Status code: {response.status_code}")

    # function to store the image which is read from the table 
    def db_img(name, data): 
        # out variable set to null 
        out = None
        s = name[len(name)-12:len(name)]

        if not os.path.exists('face_database/'+s):
            os.makedirs('face_database/'+s)
            
        try:             

            # creating files in output folder for writing in binary mode 
            out = open('face_database/'+s+'/'+name+'.jpg', 'wb') 
            
            # writing image data 
            out.write(data) 
            
        # if exception raised 
        except IOError: 
            sys.exit(1) 
            
        # closing output file object 
        finally: 
            out.close() 
