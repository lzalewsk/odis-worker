#!/usr/bin/env python
import pika
import time
import pymongo
import json
from multiprocessing import Process
from datetime import datetime

#GLOBALS
USER = 'odis'
PASSWD = '!QAZ2wsx'
HOST = 'localhost'
SERVER = 'odis.pluslab.pl'
PORT = 5672
NO_OF_WORKERS = 3

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

	client = pymongo.MongoClient('localhost', 27017)
	db = client.odisdb
	coll = db.records
	#recordid = coll.insert_one(json.loads(body)).inserted_id
	recordid = coll.insert_one(bj).inserted_id
	print recordid
	    
	print(" [x] Done")
	client.close()
	ch.basic_ack(delivery_tag = method.delivery_tag)

# metoda podlaczenia do RabbitMQ
def mRabbitMQConnector():
	credentials = pika.PlainCredentials(USER,PASSWD)
	parameters = pika.ConnectionParameters(HOST,
					       PORT,
					       SERVER,
					       credentials)

	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.queue_declare(queue='task_queue', durable=True)
	print(' [*] Waiting for messages. To exit press CTRL+C')


	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(callback,
			      queue='task_queue')

	channel.start_consuming()
	print(' [*] BYE')

if __name__ == '__main__':
	process = []
	for i in range(0,NO_OF_WORKERS):
    		p = Process(target=mRabbitMQConnector)
		process.append(p)
		process[i].start()
		print "GO"
