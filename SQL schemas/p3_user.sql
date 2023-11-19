CREATE TABLE `P3_user` (
  `user_id` varchar(4) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `surname` varchar(45) DEFAULT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `address` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `document_id` varchar(9) DEFAULT NULL,
  `JMBG` varchar(13) DEFAULT NULL,
  `note` text,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
