#!/usr/bin/env python
import pika 
import sys
from kazoo.client import KazooClient,KazooException
import logging
logging.basicConfig()

zk=KazooClient(
	hosts='127.0.0.1:2181'#don't forget to map ports to local_machine when using docker
)
zk.start()

if not(zk.exists("/master")):
	zk.create("/master",b"master")

if not(zk.exists("/master/child")):
	print("CHILD Creation")
	zk.create("/master/child",b"child")#create children using path

@zk.ChildrenWatch("/master")
def watch_children(children):
    print("Children are now: %s" % children)

#data, stat = zk.get("/master")
'''
if not(zk.exists("/master/child")):
	print("CHILD Creation")
	#zk.create("/master/child",b"child")#create children using path
'''
if zk.exists("/master"):
	print("AINVAYIIIII")
	print(zk.get_children("/master"))
#print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))
zk.delete("/master",recursive=True)
print(zk.exists("/master"))
print(zk.exists("/child"))
print(zk.exists("/master/child"))
zk.create("/master",b"master")
zk.create("/worker",b"worker")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='rideshare', exchange_type='direct')
#channel.exchange_declare(exchange='rideshare', exchange_type='direct')

#severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
print("Start Sending")
try:
	while(True):
		messtype,message=input().split()
		#message = 'Hello World!'
		if messtype=="W":
			channel.basic_publish(
				exchange='rideshare', routing_key='writer', body=message)
			print(" [x] Write %r:%r" % ('writer', message))
		else:
			channel.basic_publish(
				exchange='rideshare', routing_key='reader', body=message)
			print(" [x] Read %r:%r" % ('reader', message))
except:
	pass
finally:
	connection.close()
	zk.stop()