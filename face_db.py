import psycopg2
import os
from dotenv import load_dotenv
import pickle


load_dotenv()

database_host = os.getenv("DATABASE_HOST")
database_name = os.getenv("DATABASE_NAME")
database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASSWORD")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=database_host,
    database=database_name,
    user="postgres",
    password="Face2023Taqsim"
)


class FaceDB:
    def __init__(self):
        self.last_encoding_date = None
        self.encodings = None
        self.known_face_encodings = []
        self.known_face_names = []

    def get_encodings(self):
        try:
            print("get_encodings")
            sql_select_Query = "select encodings_date, known_face_encodings, known_face_names from face_encodings order by id desc LIMIT 1"
            
            conn = psycopg2.connect(
                host=database_host,
                database=database_name,
                user="postgres",
                password="Face2023Taqsim"
            )
            
            cursor = conn.cursor()
            cursor.execute(sql_select_Query)

            # get all records
            records = cursor.fetchall()
            for row in records:
                self.last_encoding_date = row[0]
                self.known_face_encodings = pickle.loads(row[1])
                self.known_face_names = row[2]

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            conn.close()  
            return self.last_encoding_date, self.known_face_encodings, self.known_face_names
        

        
    def insert_encodings(self, dt, known_face_encodings, known_face_names):
        try:
            print("insert_encodings")
            conn = psycopg2.connect(
                host=database_host,
                database=database_name,
                user="postgres",
                password="Face2023Taqsim"
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO face_encodings (encodings_date, known_face_encodings, known_face_names)
                VALUES (%s, %s, %s)
            """, (dt, pickle.dumps(known_face_encodings), known_face_names)
            )
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            conn.close()  


    def insert_face_images(self, timestamp, name, image_data):
        try:
            print("insert_face_images")
            conn = psycopg2.connect(
                host=database_host,
                database=database_name,
                user="postgres",
                password="Face2023Taqsim"
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO face_images (time, name, image_data)
                VALUES (%s, %s, %s)
            """, (timestamp, name, psycopg2.Binary(image_data)))
            conn.commit()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            conn.close()  
        # Insert the details into the PostgreSQL database
                    

    try:
        conn = psycopg2.connect(
            host=database_host,
            database=database_name,
            user="postgres",
            password="Face2023Taqsim"
        )
            
        cur = conn.cursor()

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
        conn.commit()

        cur = conn.cursor()

        # Create the face_temp table if it doesn't exist face_encodings (encodings_date, known_face_encodings, known_face_names)
        cur.execute("""        
                CREATE TABLE IF NOT EXISTS face_encodings(
                id SERIAL PRIMARY KEY,
                encodings_date TIMESTAMP,
                known_face_encodings BYTEA,
                known_face_names TEXT[]        
            )
        """)
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        conn.close()    
