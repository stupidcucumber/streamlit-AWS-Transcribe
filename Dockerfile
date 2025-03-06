FROM python:3.12-bullseye

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y


WORKDIR /app

ADD requirements.txt /app/
RUN pip3 install --no-cache -r requirements.txt

COPY . /app/


CMD ["streamlit", "run", "/app/main.py"]