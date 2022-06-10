FROM ubuntu
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 8000
#CMD ["python3", "manage.py", "migrate"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bookstore_project.wsgi:application"]
