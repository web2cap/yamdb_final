FROM python:3.7-slim

RUN mkdir /app
COPY . /app
WORKDIR /app/api_yamdb/
RUN pip3 install -r requirements.txt 


CMD ["gunicorn", "wsgi:application", "--bind", "0:8000" ]