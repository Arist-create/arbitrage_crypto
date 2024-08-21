FROM --platform=amd64 python:3.10-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY . /app/
RUN pip install -r requirements.txt
