# syntax=docker/dockerfile:1

FROM python:alpine3.13

WORKDIR /app

#ENV FLASK_APP=api/main.py
#ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app

RUN apk --update add git
RUN apk add musl-dev linux-headers g++  # for numpy

COPY requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY api api
EXPOSE 5000

#CMD ["flask", "run"]
CMD ["python3", "api/main.py"]