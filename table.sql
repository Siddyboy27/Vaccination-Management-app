-- MySQL dump 10.13  Distrib 5.7.22, for Linux (x86_64)
--
-- Host: localhost    Database: mymusic
-- ------------------------------------------------------
-- Server version	5.7.22-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `songs`
--

DROP TABLE IF EXISTS `songs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;


--
-- Dumping data for table `songs`
--
-- Table structure for table `songs_list`
--


DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `che` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

create table `playlist`(
`playlist_id` int not null auto_increment, 
`title` varchar(255) not null, 
`user_id` int not null, 
primary key(`playlist_id`), 
foreign key(`user_id`) references users(`id`) );

create table `tracks`( 
`song_id` int auto_increment, 
`title` varchar(255) not null, 
`link` varchar(255) not null,  

`album_id` int, 
`artist_id` int not null,
`band_id` int,
 primary key(`song_id`), 
  
 foreign key(`artist_id`) references artists(`artist_id`),
 foreign key(`band_id`) references band(`band_id`));
 
 create table `artists`( 
 `artist_id` int auto_increment not null, 
 `A_name` varchar(1000) not null, 
 `A_role` varchar(30),
 `band_id` int,
 primary key(`artist_id`),
 foreign key(`band_id`) references band(`band_id`));
 
  create table `band`( 
 `band_id` int auto_increment not null, 
 `B_name` varchar(1000) not null, 
 `NOM` int not null,
 primary key(`band_id`) );
 
 create table Album( 
`album_id` int auto_increment, 
`album_name` varchar(255) not null, 
`Release_year` varchar(255) not null, 
`artist_id` int not null,
`band_id` int,
 primary key(`album_id`), 
 foreign key(`artist_id`) references artists(artist_id),
 foreign key(`band_id`) references band(`band_id`));
 
 create table `track_listing`( 
 `user_id` int , 
 `playlist_id`int, 
 `song_id` int,
  foreign key(`user_id`) references users(`id`),
  foreign key(`playlist_id`) references playlist(`playlist_id`),
  foreign key(`song_id`) references tracks(`song_id`));

--
-- Dumping data for table `users`

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-09  1:11:01
