FROM python:3.11.0

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

RUN adduser --disabled-password --no-create-home django

# EXPOSE 8000

USER django

# CMD ["uwsgi", "--socket", ":9000", "--workers", "4", "--master", "--enable-threads", "--module", "app.wsgi"]

COPY ./entrypoint.sh /

ENTRYPOINT ["sh", "/entrypoint.sh"]

