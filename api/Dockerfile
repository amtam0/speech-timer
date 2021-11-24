
FROM python:3.8
USER root

# Set default port.
ENV PORT 80
RUN apt-get update
RUN apt-get install nano ffmpeg -y

WORKDIR /app
COPY app/ .

RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate
RUN pip install -r requirements.txt
RUN pip install pip-autoremove

RUN python download_models.py
# Run the web service using gunicorn.
CMD . /opt/venv/bin/activate && exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 main:app