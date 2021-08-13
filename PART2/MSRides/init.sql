CREATE TABLE `ride`(
         `rideid` BIGINT AUTO_INCREMENT PRIMARY KEY,
         `timestamp` DATETIME NOT NULL,
         `created_by` VARCHAR(255) BINARY NOT NULL,
         `source` INT NOT NULL,
         `destination` INT NOT NULL,
     );
	
CREATE TABLE `rideuser`(
         `rideid` BIGINT NOT NULL,
         `username` VARCHAR(255) BINARY NOT NULL,
         FOREIGN KEY (`rideid`) REFERENCES ride(rideid) ON DELETE CASCADE,
         PRIMARY KEY(rideid,username)
     );