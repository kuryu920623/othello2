create database if not exists `othello2` character set utf8mb4;

grant all on *.* to sora identified by 'sora';
CREATE USER 'othello2'@'localhost' IDENTIFIED BY 'othello2';
grant all on *.* to othello2@localhost identified by 'othello2';
