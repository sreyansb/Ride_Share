import mysql.connector

#creating a new schema/database

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
    )

myc=mydb.cursor()
myc.execute("DROP DATABASE IF EXISTS usersDB")
myc.execute("CREATE DATABASE usersDB")
myc.close()
mydb.close()


mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="usersDB")

myc=mydb.cursor()

#VERY IMPORTANT: MYSQL is not case sensitive(everything in lower case). So use binary so that case sensitivity comes in
s='''CREATE TABLE `user`(
        `username` VARCHAR(255) BINARY NOT NULL PRIMARY KEY,
        `password` VARCHAR(40) NOT NULL
        );'''

#myc.execute(s+k+j,multi=True)
myc.execute(s)
#res=myc.execute("SHOW TABLES")
#print(res.fetchall())