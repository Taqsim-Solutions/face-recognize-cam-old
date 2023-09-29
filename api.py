import numpy as np
import requests
import json

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
