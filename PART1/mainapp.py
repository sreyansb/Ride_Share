from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
import json
import mysql.connector
import requests

app = Flask(__name__)
api = Api(app)


class AddUser(Resource):
	def put(self):
		req_json = request.get_json()
		username = req_json["username"]
		password = req_json["password"]
		where = "`username`='"+username+"'"
		msgbody = {"table": "user", "column": ["username"], "where": where}
		reply = requests.post(
			"http://127.0.0.1:5000/api/v1/db/read", json=msgbody)
		ans = reply.json()
		if not(ans):
			return Response({}, status=404, mimetype="application/json")

class RemoveUser(Resource):
	def delete(self, username):
		if not(username):
			return Response({}, status=400, mimetype="application/json")
		
		wherecond = "`username`=" + str(username)
		msgbody = {"table": "ride", "column": ["rideid"], "where": wherecond}
		reply = requests.post("http://127.0.0.1:5000/api/v1/db/read", json = msgbody)
		res = reply.json()
		if res:
			mydb = mysql.connector.connect(
				host="localhost", user="root", password="root", database="rideshare")
			myc = mydb.cursor()
			query1 = "DELETE FROM ride WHERE rideid=%s"
			myc.execute(query1, (username,))
			mydb.commit()
			query2 = "DELETE FROM rideuser WHERE rideid=%s"
			myc.execute(query2, (username,))
			mydb.commit()
			return Response({}, status=204, mimetype="application/json")
			# changed status code to 204 because 200 is when message body has stuff
		else:
			return Response({}, status=400, mimetype="application/json")


class CreateRide(Resource):
	def post(self):
		req_json = request.get_json()
		username = created_by = req_json["created_by"]
		timestamp = req_json["timestamp"]
		source = req_json["source"]
		destination = req_json["destination"]


# it is suggested we always provide 'get' method
class RideApis(Resource):

    def get(self,ride_id):
        if not(ride_id):
            return Response({},status=400,mimetype="application/json")
        
        #to verify that the ride exists
        wherecond="`rideid`="+str(ride_id)
        msgbody={"table":"ride","column":["rideid"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans=reply.json()
        if not(ans):
            return Response({},status=404,mimetype="application/json")
        
        #to get the rideID, created_by, Timestamp, source and destination of the ride
        msgbody={"table":"ride","column":["rideid","created_by","source","destination","timestamp"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans1=reply.json()

        #to get all the users of the ride
        msgbody={"table":"rideuser","column":["username"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans2=reply.json()

        di={}
        di["rideId"]=ans1[0]["rideid"]
        di["Created_By"]=ans1[0]["created_by"]
        di["Timestamp"]=ans1[0]["timestamp"]
        di["source"]=ans1[0]["source"]
        di["destination"]=ans1[0]["destination"]
        di["users"]=[]
        for i in ans2:
            di["users"].append(i["username"])
    
        return Response(json.dumps(di),status=200,mimetype="application/json")
    
    def post(self,ride_id):
        if not(ride_id):
            return Response({},status=400,mimetype="application/json")
        
        #to check if ride exists
        wherecond="`rideid`="+str(ride_id)
        msgbody={"table":"ride","column":["rideid"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans=reply.json()
        if not(ans):
            return Response({},status=404,mimetype="application/json")
        
        #to check if user_name exists in the body of the message
        username=request.get_json()["username"]
        wherecond="`username`='"+username+"'"# have to give quotes around username or string types
        msgbody={"table":"user","column":["username"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans=reply.json()
        if not(ans):
            return Response({},status=404,mimetype="application/json")
        
        wherecond="`username`='"+username+"' AND "+"`rideid`="+str(ride_id)
        msgbody={"table":"rideuser","column":["rideid","username"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        ans=reply.json()
        if ans:
            #if already found=>it was already there => bad request
            return Response({},status=400,mimetype="application/json")
        else:
            msgbody={"table":"rideuser","column":["rideid","username"],"insert":[ride_id,username]}
            reply=requests.post("http://127.0.0.1:5000/api/v1/db/write",json=msgbody)
    
    def delete(self,ride_id):
        #return Response({},status=400,mimetype="application/json")
        if not(ride_id):
            return Response({},status=400,mimetype="application/json")
        wherecond="`rideid`="+str(ride_id)
        msgbody={"table":"ride","column":["rideid"],"where":wherecond}
        reply=requests.post("http://127.0.0.1:5000/api/v1/db/read",json=msgbody)
        res=reply.json()
        if res:
            mydb=mysql.connector.connect(host="localhost",user="root",password="root",database="rideshare")
            myc=mydb.cursor()
            query1 = "DELETE FROM ride WHERE rideid=%s"
            myc.execute(query1,(ride_id,))
            mydb.commit()
            query2 = "DELETE FROM rideuser WHERE rideid=%s"
            myc.execute(query2,(ride_id,))
            mydb.commit()
            return Response({},status=204,mimetype="application/json")
            #changed status code to 204 because 200 is when message body has stuff
        else:
            return Response({},status=400,mimetype="application/json")


class WriteDB(Resource):

	def get(self):
		return Response({}, status=405, mimetype="application/json")

	def post(self):
		mydb = mysql.connector.connect(
			host="localhost", user="root", password="root", database="rideshare")
		myc = mydb.cursor()
		data = request.get_json()

		data_insert = data["insert"]
		data_insert = ["'"+i+"'" for i in data_insert]
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

		return Response({}, status=204, mimetype="application/json")


class ReadDB(Resource):

	def get(self):
		return Response({}, status=405, mimetype="application/json")

	def post(self):
		mydb = mysql.connector.connect(
			host="localhost", user="root", password="root", database="rideshare")
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
				di[data["column"][j]] = i[j]
			final_res.append(di.copy())
			del di

		return Response(json.dumps(final_res), status=200, mimetype="application/json")


api.add_resource(RemoveUser, "/api/v1/users/<string:username>")
api.add_resource(AddUser, "/api/v1/users")
# if ride_id is not given, it sends a 404 error
api.add_resource(RideApis, "/api/v1/rides/<int:ride_id>")
api.add_resource(CreateRide, "/api/v1/rides")
api.add_resource(WriteDB, "/api/v1/db/write")
api.add_resource(ReadDB, "/api/v1/db/read")

if __name__ == "__main__":
	app.run(debug=True)
