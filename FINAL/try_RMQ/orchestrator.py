#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='rideshare', exchange_type='direct')

#severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = 'Hello World!'
channel.basic_publish(
    exchange='rideshare', routing_key='writer', body=message)
print(" [x] Sent %r:%r" % ('writer', message))
connection.close()