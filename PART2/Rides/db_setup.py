import mysql.connector

#creating a new schema/database

mydb=mysql.connector.connect(
    host="ride_db_service",
    user="root",
    password="root"
    )

myc=mydb.cursor()
myc.execute("DROP DATABASE IF EXISTS ridesDB")
myc.execute("CREATE DATABASE ridesDB")
myc.close()
mydb.close()


mydb=mysql.connector.connect(
    host="ride_db_service",
    user="root",
    password="root",
    database="ridesDB")

myc=mydb.cursor()

#VERY IMPORTANT: MYSQL is not case sensitive(everything in lower case). So use binary so that case sensitivity comes in
k='''CREATE TABLE `ride`(
         `rideid` BIGINT AUTO_INCREMENT PRIMARY KEY,
         `timestamp` DATETIME NOT NULL,
         `created_by` VARCHAR(255) BINARY NOT NULL,
         `source` INT NOT NULL,
         `destination` INT NOT NULL,
     );'''
j='''CREATE TABLE `rideuser`(
         `rideid` BIGINT NOT NULL,
         `username` VARCHAR(255) BINARY NOT NULL,
         FOREIGN KEY (`rideid`) REFERENCES ride(rideid) ON DELETE CASCADE,
         PRIMARY KEY(rideid,username)
     );'''
#myc.execute(s+k+j,multi=True)
myc.execute(k)
myc.execute(j)
#res=myc.execute("SHOW TABLES")
#print(res.fetchall())

