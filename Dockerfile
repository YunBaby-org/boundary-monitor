FROM python:3.8

COPY ./requirements.txt /app/requirements.txt 

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENV DB_HOST=127.0.0.1
ENV DB_PORT=5432
ENV DB_PASS=password
ENV RABBITMQ_USER=guest
ENV RABBITMQ_PASS=guest
ENV RABBITMQ_PORT=5672
ENV RABBITMQ_HOST=127.0.0.1

CMD [ "python", "./main.py" ]