# -*- coding: utf-8 -*-
import os
import pika
from pika import exceptions
import time
import pymongo
import json
from datetime import datetime

__author__ = 'Lukasz Zalewski / plus.pl'

#GLOBALS
#RabbitMQ
RABBITMQ_MAIN_HOST = str(os.environ['RABBITMQ_MAIN_HOST'])
RABBITMQ_MAIN_PORT = int(os.environ['RABBITMQ_MAIN_PORT'])
RABBITMQ_BCK_HOST = str(os.environ['RABBITMQ_BCK_HOST'])
RABBITMQ_BCK_PORT = int(os.environ['RABBITMQ_BCK_PORT'])
VIRTUAL_HOST = os.environ['VIRTUAL_HOST']
RMQ_USER = os.environ['RMQ_USER']
RMQ_PASSWD = os.environ['RMQ_PASSWD']
QUEUE = os.environ['QUEUE']
#Mongo
MONGO_RS1_HOST = os.environ['MONGO_RS1_HOST']
MONGO_RS1_PORT = os.environ['MONGO_RS1_PORT']
MONGO_RS2_HOST = os.environ['MONGO_RS2_HOST']
MONGO_RS2_PORT = os.environ['MONGO_RS2_PORT']
MONGO_USER = os.environ['MONGO_USER']
MONGO_PASSWD = os.environ['MONGO_PASSWD']

# metoda nasluchuje na odbir danych po otrzymaniu wysyla do bazy MongoDB
def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        bj = json.loads(body)
        try:
                bj['TIMESTAMP'] = datetime.strptime(bj['TIMESTAMP'],"%Y-%m-%dT%H:%M:%S")
        except:
                bj['TIMESTAMP'] = datetime.strptime("1970-01-01T00:00:00","%Y-%m-%dT%H:%M:%S")
                pass

        bj['RECORD_TIME'] = datetime.now()

        #client = pymongo.MongoClient('localhost', 27017)
        client = pymongo.MongoClient([MONGO_RS1_HOST+':'+MONGO_RS1_PORT,MONGO_RS2_HOST+':'+MONGO_RS2_PORT])
        db = client.odisdb
	db.authenticate(MONGO_USER, MONGO_PASSWD)
        coll = db.records
        #recordid = coll.insert_one(json.loads(body)).inserted_id
        recordid = coll.insert_one(bj).inserted_id
        print recordid

        print(" [x] Done")
        client.close()
        ch.basic_ack(delivery_tag = method.delivery_tag)

def connect_to_rabbit_node(connectionParams):
    # polacz sie z pierwszym dostepnym nodem rabbitowym z listy
    i=-1
    while True:
        try:
            # id of rabbit node on the list
            i=(i+1)%len(connectionParams)

            # Step #1: Connect to RabbitMQ using the default parameters
            connection = pika.BlockingConnection(connectionParams[i])
            return connection

        except exceptions.AMQPConnectionError as e:
            # print "Rabbitmq Connection error " + e.message
            pass
        except:
            print "Unexpected error:"
            raise

# metoda podlaczenia do RabbitMQ
def mRabbitMQConnector():
        connectionParams = []
        credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASSWD)
        main_parameters = pika.ConnectionParameters(RABBITMQ_MAIN_HOST,
                                               RABBITMQ_MAIN_PORT,
                                               VIRTUAL_HOST,
                                               credentials)
        #backup connection parameters
        bck_parameters = pika.ConnectionParameters(RABBITMQ_BCK_HOST,
                                               RABBITMQ_BCK_PORT,
                                               VIRTUAL_HOST,
                                               credentials)
        connectionParams.append(main_parameters)
        connectionParams.append(bck_parameters)

        #connection = pika.BlockingConnection(main_parameters)
        connection = connect_to_rabbit_node(connectionParams)

        channel = connection.channel()

        channel.queue_declare(queue=QUEUE, durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')


        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                              queue=QUEUE)

        channel.start_consuming()
        print(' [*] BYE')

if __name__ == '__main__':
	mRabbitMQConnector()
	print "GO"
