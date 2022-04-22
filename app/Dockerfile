# Pull base image
FROM balenalib/raspberry-pi-python:3.9

COPY ./container /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN mkdir /vol

EXPOSE 5000

ENTRYPOINT ["python3", "run.py"]
