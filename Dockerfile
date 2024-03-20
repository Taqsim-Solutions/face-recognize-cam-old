FROM python:3.10.7

WORKDIR /app

COPY . .

RUN --mount=type=cache,target=target=/var/cache/apt \
    apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
#["python","/app/face_db.py"] & 
CMD ["python","-u","/app/face_db.py"] &  ["python","-u","/app/face_cam.py"]
