import mysql.connector

#creating a new schema/database

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
    )

myc=mydb.cursor()
myc.execute("DROP DATABASE IF EXISTS rideshare")
myc.execute("CREATE DATABASE rideshare")
myc.close()
mydb.close()


mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="rideshare")

myc=mydb.cursor()

s='''CREATE TABLE `user`(
        `username` VARCHAR(255) NOT NULL PRIMARY KEY,
        `password` VARCHAR(40) NOT NULL
        );'''
k='''CREATE TABLE `ride`(
         `rideid` BIGINT AUTO_INCREMENT PRIMARY KEY,
         `timestamp` DATETIME NOT NULL,
         `created_by` VARCHAR(255) NOT NULL,
         `source` INT NOT NULL,
         `destination` INT NOT NULL,
          FOREIGN KEY (`created_by`) REFERENCES `user`(`username`)
     );'''
j='''CREATE TABLE `rideuser`(
         `rideid` BIGINT NOT NULL,
         `username` VARCHAR(255) NOT NULL,
         FOREIGN KEY (`rideid`) REFERENCES ride(rideid),
         FOREIGN KEY (`username`) REFERENCES user(username),
         PRIMARY KEY(rideid,username)
     );'''
#myc.execute(s+k+j,multi=True)
myc.execute(s)
myc.execute(k)
myc.execute(j)
#res=myc.execute("SHOW TABLES")
#print(res.fetchall())

