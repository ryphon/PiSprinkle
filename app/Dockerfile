# Pull base image
#FROM balenalib/raspberrypi0-2w-64-python:3.9-buster
FROM python:3.9.12

COPY ./container /app
WORKDIR /app
RUN apt-get update -y && apt-get install build-essential
RUN pip install -r requirements.txt
RUN apt-get remove build-essential -y && apt-get autoremove -y && apt-get autoclean -y
RUN mkdir /vol

EXPOSE 5000

ENTRYPOINT ["python3", "run.py"]
