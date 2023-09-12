import psycopg2

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="185.183.243.254",
        database="face",
        user="postgres",
        password="postgres"
    )
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

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    conn.close()
