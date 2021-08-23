#!/usr/bin/env python
import pika
import sys
from kazoo.client import KazooClient,KazooException
import logging
import os
logging.basicConfig()
zk=KazooClient(
	hosts='127.0.0.1:2181'#don't forget to map ports to local_machine when using docker
)
zk.start()

def master_tasks(message):
	print("Master_Tasks")

def slave_tasks(message):
	print("Slave_Tasks")

def promote_to_master(message):
	print("Master Promotion")



def check_master_or_slave(ch, method, properties, body):
	if method.routing_key=="writer":
		print("Writer:",body,os.getpid())
	else:
		print("Reader:",body,os.getpid())
	

#ROUND ROBIN FASHION: pass one by one, if condition met=> delete the message
#or continue with other processes

def startkaro(channel):#returns a channel based on what we need

	if len(zk.get_children("/master"))==0:#no master->has to be created
		print("Master_Creation")
		newmaster=f"/master/{str(os.getpid())}"
		zk.create(newmaster)
		result = channel.queue_declare(queue='writer', exclusive=True)
		queue_name = result.method.queue
		channel.queue_bind(
			exchange='rideshare', queue=queue_name, routing_key='writer')
		return queue_name
	else:
		print("Worker_Creation")
		newworker=f"/worker/{str(os.getpid())}"
		zk.create(newworker)
		result = channel.queue_declare(queue='reader', exclusive=True)
		queue_name = result.method.queue
		channel.queue_bind(
			exchange='rideshare', queue=queue_name, routing_key='reader')
		return queue_name
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='rideshare', exchange_type='direct')
queue_name=startkaro(channel)

channel.basic_consume(
    queue=queue_name, on_message_callback=check_master_or_slave, auto_ack=True)
channel.start_consuming()


zk.stop()