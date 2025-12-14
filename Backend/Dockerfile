
FROM python:3.11-alpine

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
ENV DEBUG=True
ENV ENVIRONMENT=production


WORKDIR /usr/src/app

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    postgresql-dev \
    musl-dev \
    zlib-dev \
    jpeg-dev \
    bash \
    curl

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --root-user-action=ignore



COPY . .

COPY wait-for-redis.sh /wait-for-redis.sh
RUN chmod +x /wait-for-redis.sh


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
