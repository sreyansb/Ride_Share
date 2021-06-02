from flask import Flask, request, Response
from flask_restful import Resource, Api
import json
import mysql.connector
import requests
import datetime #for usage in listing the rides
import re

app = Flask(__name__)
api = Api(app)


class AddUser(Resource):
	def put(self):

		req_json = request.get_json()
		try:
			username = req_json["username"]
			password = req_json["password"]
		except:
			return Response({}, status = 400, mimetype = "application/json")
		
		#to check if password is SHA1		
		if not (re.match(r"^[a-fA-F0-9]{40}$",password)):
				return Response({}, status = 400, mimetype = "application/json") 

		where = "`username`='"+username+"'"
		msgbody = {"table": "user", "column": ["username"], "where": where}
		reply = requests.post(
			"http://127.0.0.1:5000/api/v1/db/read", json = msgbody)	
		if reply.status_code!=200:
    			return Response({}, status = 500, mimetype="application/json")
		ans = reply.json()

		if ans:
			# user already exists
			return Response({}, status = 400, mimetype = "application/json")
		else:
			msgbody = {"insert": [username, password], "column": ["username", "password"], "table": "user"}
			reply = requests.post("http://127.0.0.1:5000/api/v1/db/write", json = msgbody)
			if reply.status_code!=201:
    				return Response({}, status = 500, mimetype="application/json")
			return Response({}, status = 201, mimetype = "application/json")


class RemoveUser(Resource):
	def delete(self, username):

		where = "`username`=" + str("'" + username + "'")
		msgbody = {"table": "user", "column": ["username"], "where": where}
		reply = requests.post("http://127.0.0.1:5000/api/v1/db/read", json = msgbody)
		if reply.status_code!=200:
    			return Response({}, status = 500, mimetype="application/json")
		res = reply.json()

		if res:
			mydb = mysql.connector.connect(host="localhost", user="root",password="root",database="rideshare")
			myc = mydb.cursor()
			query1 = "DELETE FROM `user` WHERE `username` = %s"
			myc.execute(query1, (username,))
			mydb.commit()
			return Response({}, status = 204, mimetype="application/json")
			# changed status code to 204 because 200 is when message body has stuff
		else:
			return Response({}, status = 400, mimetype="application/json")

class WriteDB(Resource):

	def get(self):
		return Response({}, status=405, mimetype="application/json")

	def post(self):
		mydb = mysql.connector.connect(
			host="localhost", user="root",password="root",database="rideshare")
		myc = mydb.cursor()
		data = request.get_json()

		data_insert = data["insert"]
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
		#return Response({}, status=400, mimetype="application/json")
		mydb = mysql.connector.connect(
			host="localhost", user="root",password="root",database="rideshare")
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


api.add_resource(RemoveUser, "/api/v1/users/<string:username>")
api.add_resource(AddUser, "/api/v1/users")
