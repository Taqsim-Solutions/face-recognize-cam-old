import psycopg2
import os
from dotenv import load_dotenv
import pickle
import sys 
import api 
from api import FaceApi

load_dotenv()

database_host = os.getenv("DATABASE_HOST")
database_name = os.getenv("DATABASE_NAME")
database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASSWORD")

def connect_db(): 
        # Connection variable set to null 
        con = None
    
        try: 
            # Connecting to database using the PostgreSQL adapter 
            con = psycopg2.connect(host=database_host, database=database_name, user='postgres', 
                                password='Face2023Taqsim') 
            
            # Creating the cursor object to run queries 
            cur = con.cursor() 
            
        # Calling rollback method if exception is raised 
        except psycopg2.DatabaseError: 
            if con: 
                con.rollback() 
            sys.exit(1) 
            
        # returning the cursor and connection object 
        return cur, con 

class FaceDB:
    def __init__(self):
        self.last_encoding_date = None
        self.encodings = None
        self.known_face_encodings = []
        self.known_face_names = []

        
    def save_image_files():        
        # calling the connect_db function for connection & cursor object 
        print("save_image_files")
        cur, con = connect_db() 
        try: 
            # Cursor object holding all image data from table 
            cur.execute("SELECT name, image_data FROM face_images") 
            for row in cur.fetchall():                 
                # the image data is written to file using db_img() for viewing 
                FaceApi.db_img(row[0], row[1])

        except(Exception, psycopg2.Error) as e: 
            # Print exception 
            print(e) 
            
        finally: 
            # Closing connection 
            con.close()

    def get_encodings(self):
        cur, con = connect_db() 
        try:
            print("get_encodings")
            sql_select_Query = "select encodings_date, known_face_encodings, known_face_names from face_encodings order by id desc LIMIT 1"
                      
            cur.execute(sql_select_Query)

            # get all records
            records = cur.fetchall()
            for row in records:
                self.last_encoding_date = row[0]
                self.known_face_encodings = pickle.loads(row[1])
                self.known_face_names = row[2]

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            con.close()  
            return self.last_encoding_date, self.known_face_encodings, self.known_face_names
        

        
    def insert_encodings(self, dt, known_face_encodings, known_face_names):
        cur, con = connect_db() 
        try:
            print("insert_encodings")

            cur.execute("""
                INSERT INTO face_encodings (encodings_date, known_face_encodings, known_face_names)
                VALUES (%s, %s, %s)
            """, (dt, pickle.dumps(known_face_encodings), known_face_names)
            )
            con.commit()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            con.close()  


    def insert_face_images(self, timestamp, name, image_data):
        cur, con = connect_db() 
        try:            
            cur.execute("""
                INSERT INTO face_images (time, name, image_data)
                VALUES (%s, %s, %s)
            """, (timestamp, name, psycopg2.Binary(image_data)))
            con.commit()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            con.close()  
        # Insert the details into the PostgreSQL database
                    
    
    cur, con = connect_db() 
    try:
        # Create the face_temp table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS face_images(
                id SERIAL PRIMARY KEY,
                time TIMESTAMP,
                name VARCHAR(255),
                guid UUID,
                image_data BYTEA
            )
        """)
        con.commit()

        # Create the face_temp table if it doesn't exist face_encodings (encodings_date, known_face_encodings, known_face_names)
        cur.execute("""        
                CREATE TABLE IF NOT EXISTS face_encodings(
                id SERIAL PRIMARY KEY,
                encodings_date TIMESTAMP,
                known_face_encodings BYTEA,
                known_face_names TEXT[]        
            )
        """)
        con.commit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        con.close()    
