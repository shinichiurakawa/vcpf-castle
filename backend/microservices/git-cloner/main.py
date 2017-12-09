#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import, unicode_literals

# -*- coding: utf-8 -*-

from flask import Flask
from flask import request

import os, shutil
import pika
import json
import threading

import config


def response_json(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        res = func(*args,**kwargs)
        return json.dumps(res, ensure_ascii=False, indent=2)
    return wrapper

app = Flask(__name__)


@app.route('/')
def index():
    return """
<form action="/clone" method="POST">
  URL:<br>
  <input type="text" name="url" value="https://github.com/mandbjp/dotinstalled_ruby_on_rails.git"><br><br>
  <input type="submit" value="Submit">
</form>
    """


# パラメータを引数にマッピングする
@app.route('/clone', methods=['POST'])
@response_json
def clone():
    url = request.form['url']
    body = {
        "url": url
    }
    send_mq("git_clone", body)
    return body


def send_mq(queue, body):
    import pika

    credentials = pika.PlainCredentials('rabbit_test', 'rabbit_test') if config.release else None
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_mq_host(), credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_publish(exchange='',
                          routing_key=queue,  # TODO: routing_key とは？
                          body=json.dumps(body))
    print(" [x] Sent ")
    connection.close()


def shell(cmd, path):
    print("shell", cmd, "@", path)
    import subprocess
    ret = subprocess.check_output(cmd.split(" "), cwd=path)
    print(ret)
    return ret


class MqReceiver(threading.Thread):
    def __init__(self):
        super(MqReceiver, self).__init__()

    def run(self):
        credentials = pika.PlainCredentials('rabbit_test', 'rabbit_test') if config.release else None
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_mq_host(), credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='git_clone')

        print(' [*] Waiting for messages. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            body = json.loads(body)
            url = body["url"]

            import hashlib
            hash = hashlib.md5(url).hexdigest()
            clone_path = "/tmp/{hash}/".format(hash=hash)
            if os.path.exists(clone_path):
                print("removing path", clone_path)
                shutil.rmtree(clone_path)
            os.makedirs(clone_path)
            shell("git clone {url}".format(url=url), clone_path)
            # send_mq("")

        channel.basic_consume(callback, queue='git_clone', no_ack=True)

        channel.start_consuming()


def get_mq_host():
    host = str(config.db_host) if config.release else str("localhost")
    return host


if __name__ == '__main__':
    print("release?", config.release)

    mq_receiver = MqReceiver()
    mq_receiver.start()

    app.run(port=9999, debug=True)
