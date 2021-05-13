from flask import Flask,request,jsonify,Response
from flask_restful import Resource,Api
import json
import mysql.connector

app=Flask(__name__)
api=Api(app)

class writedb(Resource):
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
        print("HERE", s)
        myc.execute(s)
        mydb.commit()

        myc.close()
        mydb.close()

        return Response({},status=200,mimetype="application/json")

class readdb(Resource):
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
        print(s)
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
#api.add_resource(Hello,"/")
api.add_resource(square,"/square/<int:num>")

if __name__=="__main__":
    app.run(debug=True)

            
