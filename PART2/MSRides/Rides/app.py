from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
import json
import mysql.connector
import requests
import datetime #for usage in listing the rides
import re
from multiprocessing import Value

app = Flask(__name__)
numberofrequests=Value('i',0)
numberofrides=Value('i',0)
api = Api(app)

def atomicincrementer():
	with numberofrequests.get_lock():
		numberofrequests.value+=1

class CreateRide(Resource):
	def post(self):
		atomicincrementer()
		req_json = request.get_json()
		try:
			username = created_by = req_json["created_by"]
			timestamp = req_json["timestamp"]
			timestamp= datetime.datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
			timestamp=str(timestamp)
			#print(timestamp)
			source = req_json["source"]
			destination = req_json["destination"]
		except:
			return Response({}, status = 400, mimetype = "application/json")
		
		# check if the user exists
		reply = requests.get("http://users_service:5000/api/v1/users")
		if reply.status_code==204:
			return Response({}, status = 400, mimetype = "application/json")
	
		if reply.status_code!=200:
    			return Response({}, status = 500, mimetype = "application/json")
		
		res = reply.json()

		if username not in res:
			return Response({}, status = 400, mimetype = "application/json")
		
		query = {
					"insert" : [username, timestamp, source, destination], 
					"column" : ["created_by", "timestamp", "source", "destination"],
					"table" : "ride"
				}
		ans=requests.post("http://rides_service:5000/api/v1/db/write", json=query)
		if ans.status_code!=201:
				return Response({}, status = 500, mimetype = "application/json")
		# getting rideid
		where = "`created_by`=" + "'" + username + "'" + "AND `timestamp` = '" + timestamp + "' AND `source` = " + str(source) + " AND `destination` = " + str(destination)
		query = {"table" : "ride", "column" : ["rideid"], "where" : where}
		reply = requests.post("http://rides_service:5000/api/v1/db/read", json=query)
		if reply.status_code!=200:
				return Response({}, status = 500, mimetype = "application/json")
		rideid = reply.json()[0]["rideid"]

		#inserting into rideuser
		query = {
					"insert" : [rideid, username],
					"column" : ["rideid", "username"],
					"table" : "rideuser"
				}
		ans = requests.post("http://rides_service:5000/api/v1/db/write", json = query)
		if ans.status_code!=201:
				return Response({}, status = 500, mimetype = "application/json")
		with numberofrides.get_lock():
			numberofrides.value+=1
		return Response({}, status=201, mimetype="application/json")

	
	def get(self):
		atomicincrementer()
		try:
			source=request.args["source"]
		except:
			return Response({}, status=400, mimetype="application/json")
		try:
			destination=request.args["destination"]
		except:
			return Response({}, status=400, mimetype="application/json")
		
		wherecond=f"`source`={source} AND `destination`={destination} AND `timestamp`>=NOW()"
		msgbody={"table":"ride","column":["rideid","created_by","timestamp"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		ans1=reply.json()

		if reply.status_code==200:
			finallist=[]
			for i in ans1:
				di={}
				di["rideId"]=i["rideid"]
				di["username"]=i["created_by"]
				temp=(datetime.datetime.strptime(i["timestamp"],"%Y-%m-%d %H:%M:%S"))
				di["timestamp"]=str(datetime.datetime.strftime(temp,"%d-%m-%Y:%S-%M-%H"))
				finallist.append(di)
				del di
			return Response(json.dumps(finallist),status=200,mimetype="application/json")
		else:
			return Response({},status=500,mimetype="application/json")

# it is suggested we always provide 'get' method
class RideApis(Resource):

	def get(self,ride_id):
		atomicincrementer()
		if not(ride_id):
			return Response({},status=400,mimetype="application/json")
		
		#to verify that the ride exists
		wherecond="`rideid`="+str(ride_id)
		msgbody={"table":"ride","column":["rideid"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    			return Response({},status=500,mimetype="application/json")
		ans=reply.json()
		if not(ans):
			return Response({},status=404,mimetype="application/json")
		
		#to get the rideID, created_by, Timestamp, source and destination of the ride
		msgbody={"table":"ride","column":["rideid","created_by","source","destination","timestamp"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    			return Response({},status=500,mimetype="application/json")
		ans1=reply.json()

		#to get all the users of the ride
		msgbody={"table":"rideuser","column":["username"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    			return Response({},status=500,mimetype="application/json")
		ans2=reply.json()

		di={}
		di["rideId"]=ans1[0]["rideid"]
		di["Created_By"]=ans1[0]["created_by"]
		temp=(datetime.datetime.strptime(ans1[0]["timestamp"],"%Y-%m-%d %H:%M:%S"))
		di["timestamp"]=str(datetime.datetime.strftime(temp,"%d-%m-%Y:%S-%M-%H"))
		di["source"]=ans1[0]["source"]
		di["destination"]=ans1[0]["destination"]
		di["users"]=[]
		for i in ans2:
			di["users"].append(i["username"])
	
		return Response(json.dumps(di),status=200,mimetype="application/json")
	
	def post(self,ride_id):
		atomicincrementer()
		if not(ride_id):
			return Response({},status=400,mimetype="application/json")
		
		#to check if ride exists
		wherecond="`rideid`="+str(ride_id)
		msgbody={"table":"ride","column":["rideid"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    			return Response({},status=500,mimetype="application/json")
		ans=reply.json()
		if not(ans):
			return Response({},status=404,mimetype="application/json")
		
		#to check if user_name exists in the body of the message
		try:
			username=request.get_json()["username"]
		except:
			return Response({},status=400,mimetype="application/json")
		
		reply = requests.get("http://users_service:5000/api/v1/users")

		if reply.status_code==204:
			return Response({}, status = 400, mimetype = "application/json")
	
		if reply.status_code!=200:
    			return Response({}, status = 500, mimetype = "application/json")
		
		res = reply.json()

		if username not in res:
			return Response({}, status = 400, mimetype = "application/json")
		
		wherecond="`username`='"+username+"' AND "+"`rideid`="+str(ride_id)
		msgbody={"table":"rideuser","column":["rideid","username"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    			return Response({},status=500,mimetype="application/json")
		ans=reply.json()

		if ans:
			#if already found=>it was already there => bad request
			return Response({},status=400,mimetype="application/json")
		else:
			msgbody={"table":"rideuser","column":["rideid","username"],"insert":[ride_id,username]}
			reply=requests.post("http://rides_service:5000/api/v1/db/write",json=msgbody)
			if reply.status_code!=201:
    				return Response({},status=500,mimetype="application/json")
			return Response({},status=201,mimetype="application/json")
	
	def delete(self,ride_id):
		atomicincrementer()
		#return Response({},status=400,mimetype="application/json")
		if not(ride_id):
			return Response({},status=400,mimetype="application/json")
		wherecond="`rideid`="+str(ride_id)
		msgbody={"table":"ride","column":["rideid"],"where":wherecond}
		reply=requests.post("http://rides_service:5000/api/v1/db/read",json=msgbody)
		if reply.status_code!=200:
    				return Response({},status=500,mimetype="application/json")
		res=reply.json()
		if res:
			mydb=mysql.connector.connect(host="ride_db_service",user="admin",password="admin", database="ridesDB")
			myc=mydb.cursor()
			query2 = "DELETE FROM rideuser WHERE rideid=%s"
			myc.execute(query2,(ride_id,))
			mydb.commit()
			query1 = "DELETE FROM ride WHERE rideid=%s"
			myc.execute(query1,(ride_id,))
			mydb.commit()
			return Response({},status=204,mimetype="application/json")
			#changed status code to 204 because 200 is when message body has stuff
		else:
			return Response({},status=404,mimetype="application/json")


class WriteDB(Resource):

	def get(self):
		return Response({}, status=405, mimetype="application/json")

	def post(self):
		atomicincrementer()
		mydb = mysql.connector.connect(
			host="ride_db_service", user="admin",password="admin",database="ridesDB")
		myc = mydb.cursor()
		data = request.get_json()

		data_insert = data["insert"]
		#if type(i) == int dont need quotes: type(1)==int
		data_insert = ["'"+i+"'"  if type(i) != type(1) else str(i) for i in data_insert]
		columns = data["column"]
		columns = ["`"+i+"`" for i in columns]
		tablename = data["table"]

		data_insert = ", ".join(data_insert)
		# columns=",".join(columns)
		column_names = ', '.join(columns)
		# placeholders = ', '.join(['%s'] * len(columns))
		s = f'INSERT INTO `{tablename}` ({column_names}) VALUES ({data_insert});'
		myc.execute(s)
		mydb.commit()

		myc.close()
		mydb.close()

		return Response({}, status=201, mimetype="application/json")


class ReadDB(Resource):

	def get(self):
		return Response({}, status=405, mimetype="application/json")

	def post(self):
		atomicincrementer()
		#return Response({}, status=400, mimetype="application/json")
		mydb = mysql.connector.connect(
			host="ride_db_service", user="admin",password="admin",database="ridesDB")
		myc = mydb.cursor()
		data = request.get_json()

		tablename = data["table"]
		colnames = data["column"]
		columns = ["`"+i+"`" for i in colnames]
		condition = data["where"]
		columns = ', '.join(columns)
		# has to be formatted string, cant give normal mysql statements
		s = f"SELECT {columns} FROM `{tablename}` WHERE {condition};"
		res = myc.execute(s)
		# it is myc.fetchone()/fetchall and not res.fetchone()
		res = myc.fetchall()

		myc.close()
		mydb.close()

		final_res = []
		n = len(data["column"])
		for i in res:
			di = {}
			for j in range(n):
				di[data["column"][j]] = str(i[j])
			final_res.append(di.copy())
			del di

		return Response(json.dumps(final_res), status=200, mimetype="application/json")

class ClearDB(Resource):
	def post(self):
		atomicincrementer()
		try:
			mydb = mysql.connector.connect(host="ride_db_service", user="admin",password="admin",database="ridesDB")
			myc = mydb.cursor()
		except:
			return Response({},status=400,mimetype="application/json")
		query="DELETE FROM `rideuser`;"
		myc.execute(query)
		query="DELETE FROM `ride`;"
		myc.execute(query)
		mydb.commit()
		return Response({},status=204,mimetype="application/json")

class Incrementer(Resource):

	def get(self):
		ans=0
		with numberofrequests.get_lock():
			ans=numberofrequests.value
		return Response(json.dumps(ans),status=200,mimetype="application/json")

	def delete(self):
		with numberofrequests.get_lock():
			numberofrequests.value=0
		return Response({},status=204,mimetype="application/json")

class RideNumber(Resource):
	def get(self):
		ans=0
		with numberofrides.get_lock():
			ans=numberofrides.value
		return Response(json.dumps(ans),status=200,mimetype="application/json")

api.add_resource(Incrementer, "/api/v1/_count")

# if ride_id is not given, it sends a 404 error
api.add_resource(RideApis, "/api/v1/rides/<int:ride_id>")
api.add_resource(CreateRide, "/api/v1/rides")
api.add_resource(WriteDB, "/api/v1/db/write")
api.add_resource(ReadDB, "/api/v1/db/read")
api.add_resource(ClearDB, "/api/v1/db/clear")

