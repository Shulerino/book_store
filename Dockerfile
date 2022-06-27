
FROM ubuntu
ENV PYTHONUNBUFFERED 1
ENV DJANGO_DEBUG=""
RUN mkdir /code
RUN groupadd -r app && useradd -r app -g app
RUN mkdir /code/staticfiles
WORKDIR /code
ADD requirements.txt /code/
RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y nano
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 8000
RUN chown -R app:app /code
USER app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bookstore_project.wsgi:application"]
