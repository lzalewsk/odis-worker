# -*- coding: utf-8 -*-
import os
import pika
from pika import exceptions
import time
import toml
import pymongo
import json
from datetime import datetime

__author__ = 'Lukasz Zalewski / plus.pl'

CONF_FILE = '/conf/conf.toml'

def read_conf(CONF_FILE):
    with open(CONF_FILE) as conffile:
        conf = toml.loads(conffile.read())
    return conf

#GLOBALS
#Mongo
#MONGO_RS1_HOST = os.environ['MONGO_RS1_HOST']
#MONGO_RS1_PORT = os.environ['MONGO_RS1_PORT']
#MONGO_RS2_HOST = os.environ['MONGO_RS2_HOST']
#MONGO_RS2_PORT = os.environ['MONGO_RS2_PORT']
#MONGO_USER = os.environ['MONGO_USER']
#MONGO_PASSWD = os.environ['MONGO_PASSWD']

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

	connection_string = ''
        for mongohost in CONF['output']['mongodb']['host']:
		if connection_string != '' :
			connection_string = connection_string + ','
                connection_string = mongohost['host'] + ':' + mongohost['port']

        #client = pymongo.MongoClient([MONGO_RS1_HOST+':'+MONGO_RS1_PORT,MONGO_RS2_HOST+':'+MONGO_RS2_PORT])
	print connection_string
        if('replicaset' in CONF['output']['mongodb']):
            print 'replicaset: ', CONF['output']['mongodb']['replicaset']
            client = pymongo.MongoClient([connection_string], replicaset=CONF['output']['mongodb']['replicaset'])
        else:
            client = pymongo.MongoClient([connection_string])
        db = client.odisdb
	auth = CONF['output']['mongodb']
	print auth
	db.authenticate(auth['user'], auth['passwd'])
	#db.authenticate(MONGO_USER, MONGO_PASSWD)
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
            print "Rabbitmq Connection error " + e.message
            pass
        except:
            print "Unexpected error:"
            raise

# metoda podlaczenia do RabbitMQ
def mRabbitMQConnector():
	global CONF
	
	# Setup our ssl options
	#sslOptions = ({"ca_certs": "cacert.pem",
	#	       "certfile": "cert.pem",
	#	       "keyfile": "key.pem"})
	#sslOptions = CONF['input']['rabbitmq']['ssl_options']
        print CONF['input']['rabbitmq']['ssl_options']
        sslOptions = CONF['input']['rabbitmq']['ssl_options']

        connectionParams = []
       
        rmqaccess = CONF['input']['rabbitmq']
	credentials = pika.PlainCredentials(rmqaccess['username'], rmqaccess['password'])

	for host in CONF['input']['rabbitmq']['host']:
		connection_x = pika.ConnectionParameters(host['url']
						 ,host['port']
						 ,rmqaccess['vhost']
						 ,credentials
						 ,ssl = rmqaccess['ssl']
						 ,ssl_options = sslOptions)
		connectionParams.append(connection_x)

        #connection = pika.BlockingConnection(main_parameters)
        connection = connect_to_rabbit_node(connectionParams)

        channel = connection.channel()

        channel.queue_declare(queue=rmqaccess['queue_name'], durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')


        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                              queue=rmqaccess['queue_name'])

        channel.start_consuming()
        print(' [*] BYE')

if __name__ == '__main__':
	global CONF
	CONF = read_conf(CONF_FILE)
	mRabbitMQConnector()
	print "GO"
