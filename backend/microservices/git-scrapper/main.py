#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import, unicode_literals

# -*- coding: utf-8 -*-

import os
import pika
import json
import psycopg2

import config
import sys


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


class MqReceiver():
    def __init__(self):
        pass

    def run(self):
        credentials = pika.PlainCredentials('rabbit_test', 'rabbit_test')
        connection = None
        if config.release:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_mq_host(), credentials=credentials))
        else:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_mq_host()))

        channel = connection.channel()

        channel.queue_declare(queue='git_scrap')

        print(' [*] Waiting for messages. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            body = json.loads(body)
            print(body)
            content = search_and_load(body["path"])
            print("inserting...")
            insert_to_db(content, body["session"])
            print("committed")

        channel.basic_consume(callback, queue='git_scrap', no_ack=True)

        channel.start_consuming()


def search_and_load(path):
    scraps = []
    for filename in find_all_files(path):
        if not is_scrap_target(filename):
            continue
        content = open(filename, "r").read()
        scraps.append(content)

    print(len(scraps), "files scrapped")
    return u"\n".join(_.decode('utf-8') for _ in scraps)


def insert_to_db(scrap_content, session):
    # Connect to an existing database
    print("connecting...", get_psql_connection_info())
    conn = psycopg2.connect(get_psql_connection_info())
    print("connected!")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Query the database and obtain data as Python objects
    cur.execute("SELECT MAX(id) FROM scraping;")
    ret = cur.fetchone()
    no = ret[0] + 1
    cur.execute("INSERT INTO scraping (id, session_id, contents) VALUES (%s, %s, %s)", (no, session, scrap_content, ))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()
    return


def select_test():
    # Connect to an existing database
    conn = psycopg2.connect(get_psql_connection_info())

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Query the database and obtain data as Python objects
    cur.execute("SELECT * FROM scraping;")
    ret = cur.fetchone()
    print(ret)

    # Close communication with the database
    cur.close()
    conn.close()
    return


def is_scrap_target(filename):
    for ext in [".rb", ".py", ".java", ".md", ".txt"]:
        if filename.find(ext) != -1:
            return True
    return False


def get_mq_host():
    host = str(config.db_host) if config.release else str("localhost")
    return host


def get_psql_connection_info():
    host = str(config.db_host) if config.release else str("localhost")
    user = "interest" if config.release else str("vagrant")
    connect_info = "dbname=%s host=%s user=%s" % ("interest", host, user)
    return connect_info


def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)


if __name__ == '__main__':
    config.release = (len(sys.argv) == 2)
    print("release?", config.release)

    mq_receiver = MqReceiver()
    mq_receiver.run()
