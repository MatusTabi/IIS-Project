# Use the official Python 3.12 image from DockerHub
FROM python:3.12

ADD ./requirements.txt .

RUN pip install virtualenv
RUN virtualenv /venv
RUN . /venv/bin/activate && pip install -r requirements.txt
