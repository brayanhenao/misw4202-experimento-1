import time
import random
import threading
import requests
import logging

# endpoints = ("one", "two", "three", "four", "error")
endpoints = ("recalculate")

HOST = "http://app:5000/"

total_errors=0

def accumulate_errors():
    with open('errors','w+') as file:
        global total_errors
        total_errors+=1
        return file.write(str(total_errors))



def run():
    while True:
        try:
            target = endpoints
            r= requests.get(HOST + target, timeout=1)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.warning(f'total_errors {total_errors}')
            accumulate_errors()
            time.sleep(1)


if __name__ == "__main__":
    for _ in range(4):
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    while True:
        time.sleep(1)