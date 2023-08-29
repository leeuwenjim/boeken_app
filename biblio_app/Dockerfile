FROM python:alpine3.8
RUN python -m pip install --upgrade pip
COPY ./deploy_requirements.txt /app/deploy_requirements.txt
WORKDIR /app
RUN rm -rf /var/cache/apk/* && rm -rf /tmp/*
RUN apk update
RUN apk add build-base
RUN apk add linux-headers
RUN set -e; apk add --no-cache --virtual .build-deps gcc libc-dev mariadb-dev python3-dev postgresql-dev zlib-dev jpeg-dev musl-dev;
RUN pip install -r deploy_requirements.txt

COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT python manage.py migrate;python manage.py collectstatic --no-input;uwsgi --http :8000 --module biblio_app.wsgi
