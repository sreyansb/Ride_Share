FROM python:3.7
RUN apt-get update
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["gunicorn","-w","3","-b",":5000","-t","300","--reload","wsgi:app"]