import requests
import json
import sys
import os
from dotenv import load_dotenv

class FaceApi:
    
    load_dotenv()
    # Function to send face values to Swagger API
    def send_face_values_to_api_post(self, face_values):
        print("send_face_values_to_api")
        api_url = os.getenv("API_URL") + "face-recognitons"
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }
        error = ""
        for face_value in face_values:
            response = requests.post(api_url, json=face_value, headers=headers, verify=False)

            print("Request Body:", json.dumps(face_value, indent=2))  # Print the request body
            print("Status Code:", response.status_code)  # Print the status code

            try:
                error = response.json()
                #print("Response Body:", json.dumps(response_json, indent=2))  # Print the response body
            except json.JSONDecodeError:
                print("Failed to decode response JSON.")

            if response.status_code == 200:
                print("Face values sent successfully to the API.")
            else:
                print(f"Failed to send face values to the API. Status code: {response.status_code} and {error}")

    def send_face_values_to_api_put(self, face_values):
            print("send_face_values_to_api")            
            api_url = os.getenv("API_URL") + "face-recognitons"
            headers = {
                "accept": "*/*",
                "Content-Type": "application/json"
            }
            error = ""
            for face_value in face_values:
                print("request", requests.put(api_url, json=face_value, headers=headers, verify=False))
                response = requests.put(api_url, json=face_value, headers=headers, verify=False)

                print("Request Body:", json.dumps(face_value, indent=2))  # Print the request body
                print("Status Code:", response.status_code)  # Print the status code

                try:
                    error = response.json()
                    #print("Response Body:", json.dumps(response_json, indent=2))  # Print the response body
                except json.JSONDecodeError:
                    print("Failed to decode response JSON.")

                finally:                    
                    if response.status_code == 200:
                        print("Face values sent successfully to the API.")
                    else:
                        print(f"Failed to send face values to the API. Status code: {response.status_code} and {error}")    
                    
                    return response.status_code
            
    

 
    def authorize(self):
        #Authorization
        api_url = os.getenv("API_URL") + "authentication"
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
    def db_img(name, data, id): 

        if not os.path.exists('face_database/'+name):
            os.makedirs('face_database/'+name)
            
        try:             

            # creating files in output folder for writing in binary mode             
            file_path = os.path.join("face_database/", f"{name}/{name}_{id}.jpg")

            with open(file_path, "wb") as file:
                file.write(data)
                        
        # if exception raised 
        except IOError: 
            sys.exit(1)        
        finally:
            print(name, " saved")