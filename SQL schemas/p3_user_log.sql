CREATE TABLE `P3_user_log` (
  `user_id` varchar(4) NOT NULL,
  `membership_log` text,
  `access_log` text,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3
