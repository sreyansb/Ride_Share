from flask import Flask,request,jsonify,Response
from flask_restful import Resource,Api
import json
import mysql.connector
import requests

app=Flask(__name__)
api=Api(app)

class joinride(Resource):

    def get(self,ride_id):
        return Response({},status=405,mimetype="application/json")
    
    def post(self,ride_id):
        username=request.args["username"]

    

#it is suggested we always provide 'get' method
class rideapis(Resource):

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


class writedb(Resource):

    def get(self):
        return Response({},status=405,mimetype="application/json")
    
    def post(self):
        mydb=mysql.connector.connect(host="localhost",user="root",password="root",database="rideshare")
        myc=mydb.cursor()
        data=request.get_json()
        #print(data["idiot"])
        data_insert=data["insert"]
        data_insert=["'"+i+"'" for i in data_insert]
        columns=data["column"]
        columns=["`"+i+"`" for i in columns]
        tablename=data["table"]

        data_insert=", ".join(data_insert)
        #columns=",".join(columns)
        column_names = ', '.join(columns)
        #placeholders = ', '.join(['%s'] * len(columns))
        s = f'INSERT INTO `{tablename}` ({column_names}) VALUES ({data_insert});'
        myc.execute(s)
        mydb.commit()

        myc.close()
        mydb.close()

        return Response({},status=204,mimetype="application/json")

class readdb(Resource):

    def get(self):
        return Response({},status=405,mimetype="application/json")
    
    def post(self):
        mydb=mysql.connector.connect(host="localhost",user="root",password="root",database="rideshare")
        myc=mydb.cursor()
        data=request.get_json()
        
        tablename=data["table"]
        colnames=data["column"]
        columns=["`"+i+"`" for i in colnames]
        condition=data["where"]
        columns = ', '.join(columns)
        #has to be formatted string, cant give normal mysql statements
        s=f"SELECT {columns} FROM `{tablename}` WHERE {condition};"
        res=myc.execute(s)
        #it is myc.fetchone()/fetchall and not res.fetchone()
        res=myc.fetchall()

        myc.close()
        mydb.close()

        final_res=[]
        n=len(data["column"])
        for i in res:
            di={}
            for j in range(n):
                di[data["column"][j]]=i[j]
            final_res.append(di.copy())
            del di
        
        return Response(json.dumps(final_res),status=200,mimetype="application/json")

class square(Resource):
    def get(self,num):
        return jsonify({"answer":num*num,"status_code": 200})

api.add_resource(writedb,"/api/v1/db/write")

api.add_resource(readdb,"/api/v1/db/read")

#if ride_id is not given, it sends a 404 error
api.add_resource(rideapis,"/api/v1/rides/<int:ride_id>")

#api.add_resource(Hello,"/")
api.add_resource(square,"/square/<int:num>")

if __name__=="__main__":
    app.run(debug=True)

            
