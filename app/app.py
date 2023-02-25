import random

from flask import Flask
import pika
from flask import json
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

QUEUE_NAME = 'metricas'
RABBITMQ_USER = 'username'
RABBITMQ_PASSWORD = 'password'
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    )
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME,
                          body='http_result error')
    return response


@app.route("/recalculate")
def recalculate():
    nterms = random.randint(-1000, 10000)
    # first two terms
    n1, n2 = 0, 1
    count = 0

    # check if the number of terms is valid
    if nterms <= 0:
        return ":C", 400
    # if there is only one term, return n1
    elif nterms == 1:
        return n1
    # probability of 15% to be an error
    elif random.random() < 0.15:
        return 'Service Unavailable', 503
    # generate fibonacci sequence
    while count < nterms:
        nth = n1 + n2
        # update values
        n1 = n2
        n2 = nth
        count += 1
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME,
                          body='http_result ok')
    return str(n1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
