import time
import threading
import requests
import logging
import pika

endpoints = ("recalculate")
HOST = "http://app:5000/"
QUEUE_NAME = 'my_queue'
RABBITMQ_USER = 'username'
RABBITMQ_PASSWORD = 'password'
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672


def init_rabbitmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
    )
    channel = connection.channel()
    return channel


def run():
    channel = init_rabbitmq()
    while True:
        try:
            target = endpoints
            r = requests.get(HOST + target, timeout=1)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=str(err))


if __name__ == "__main__":
    for _ in range(4):
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    while True:
        time.sleep(1)
