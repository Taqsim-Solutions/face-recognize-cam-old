FROM python:3.10.7

WORKDIR /app

COPY . .

RUN --mount=type=cache,target=target=/var/cache/apt \
    apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

CMD ["python","/face_detect_crop_save.py"]
