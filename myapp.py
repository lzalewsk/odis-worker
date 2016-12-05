# -*- coding: utf-8 -*-
import os

__author__ = 'Lukasz Zalewski / plus.pl'

RABBITMQ_HOST = str(os.environ['RABBITMQ_HOST'])
RABBITMQ_PORT = int(os.environ['RABBITMQ_PORT'])
VIRTUAL_HOST = os.environ['VIRTUAL_HOST']
USER = os.environ['USER']
PASSWD = os.environ['PASSWD']
QUEUE = os.environ['QUEUE']

def go():
	print "RABBITMQ_HOST: ",RABBITMQ_HOST	
	print "RABBITMQ_PORT: ",RABBITMQ_PORT
	print "VIRTUAL_HOST: ",VIRTUAL_HOST	
	print "USER: ",USER
	print "PASSWD: ",PASSWD	
	print "QUEUE: ",QUEUE

if __name__ == '__main__':
	go()
