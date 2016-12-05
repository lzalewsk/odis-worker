#!/usr/bin/env python
import pika
import time
import pymongo
import json

credentials = pika.PlainCredentials('odis', '!QAZ2wsx')
parameters = pika.ConnectionParameters('localhost',
                                       5672,
                                       'odis.pluslab.pl',
                                       credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    #b = json.loads(body)

    client = pymongo.MongoClient('localhost', 27017)
    db = client.odisdb
    coll = db.records
    recordid = coll.insert_one(json.loads(body)).inserted_id
    print recordid
    
    print(" [x] Done")
    client.close()
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()

