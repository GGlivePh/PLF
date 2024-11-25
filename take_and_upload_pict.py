#!/usr/bin/python -u

import os
import time
import boto3
import json
from datetime import datetime
import RPi.GPIO as GPIO

GPIO_USED = 24
OUT_DIR = os.path.join(os.path.expanduser("~"), "SELRAS_IMAGES")
BUCKET_NAME = "selras-images"
CREDENTIAL_FILE = os.path.join(os.path.expanduser("~"), ".selras-creds")
"""
credentials = {"aws_access_key_id": "",
               "aws_secret_access_key": "",
               "endpoint_url": "https://se-sto-1.linodeobjects.com",
               "use_ssl": True
               }
"""


def take_pict(name):
    # with open(name, 'w') as f:
    #     f.write("test")
    command = f"libcamera-still --width 4056 --height 3040 -o {name} -t 3000"
    os.system(command)
    assert os.path.isfile(name)


def make_name():
    now = datetime.today()
    date = now.strftime('%Y-%m-%d')
    dir = os.path.join(OUT_DIR, date)
    basename = f"{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    os.makedirs(dir, exist_ok=True)
    name = os.path.join(dir, basename)
    return name


def upload_file(file, credentials):
    s3_ressource = boto3.resource('s3', **credentials)

    key = os.path.relpath(file, OUT_DIR)
    with open(file, 'rb') as f:
        o = s3_ressource.Object(BUCKET_NAME, key)
        o.put(Body=f)
        print(f"Saved: {key}")


def trigger_pict(arg):
    try:
        with open(CREDENTIAL_FILE, "r") as f:
            credentials = json.load(f)

        filename = make_name()
        take_pict(filename)
        upload_file(filename, credentials)
        print(filename)
    except Exception as e:
        time.sleep(1)
        raise e

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_USED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.add_event_detect(GPIO_USED, GPIO.RISING, callback=trigger_pict)
    while True:
        time.sleep(.1)
        if GPIO.input(GPIO_USED) == GPIO.HIGH:
            trigger_pict(None)
