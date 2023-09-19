import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_host = os.getenv("DATABASE_HOST")
database_name = os.getenv("DATABASE_NAME")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=database_host,
    database=database_name,
    user="postgres",
    password="postgres"
)

try:
    cur = conn.cursor()

    # Create the face_temp table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS face_recognition(
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
