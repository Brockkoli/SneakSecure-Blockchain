-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 27, 2023 at 05:21 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sneaksecure`
--

-- --------------------------------------------------------

--
-- Table structure for table `buyer`
--

CREATE TABLE `buyer` (
  `ID` int(11) NOT NULL,
  `Name` text NOT NULL,
  `Password` char(64) NOT NULL,
  `Address` varchar(10) NOT NULL,
  `Coins` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `buyer`
--

INSERT INTO `buyer` (`ID`, `Name`, `Password`, `Address`, `Coins`) VALUES
(1, 'Occifer', 'a4a048d94a855cdea007549a5e582cb250a2588e3615478f0bbb1a8f482f6c69', 'Qd451wD2Ds', 1000),
(2, 'Bobo', 'efb4aa15cd9f13d8a93a957f0d897829c28ef909625ce51c999e0cb8ab9a2601', 'sW23fDs54p', 1000),
(3, 'Chao Keng', 'fa9540f649c437018103f94cadaa340e3ce8efc06dba3d45c530d855d28896cc', 'P8i8K2kjv8', 1000),
(4, 'Wayang', 'e3aeddf7eebc7730c310a7664a94cfe98c3109cb26c65771bc1ed0c7b201a3ab', 'Jo1G6543oU', 1000);

-- --------------------------------------------------------

--
-- Table structure for table `manufacturers`
--

CREATE TABLE `manufacturers` (
  `ID` int(11) NOT NULL,
  `Name` text NOT NULL,
  `Address` varchar(10) NOT NULL,
  `Coins` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `manufacturers`
--

INSERT INTO `manufacturers` (`ID`, `Name`, `Address`, `Coins`) VALUES
(1, 'syndicate', 'Gr89o2Kmsh', 1000);

-- --------------------------------------------------------

--
-- Table structure for table `shoe`
--

CREATE TABLE `shoe` (
  `id` int(11) NOT NULL,
  `model` text NOT NULL,
  `price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `shoe`
--

INSERT INTO `shoe` (`id`, `model`, `price`) VALUES
(1, 'nike', 10),
(2, 'adidas', 20),
(3, 'puma', 30),
(4, 'ua', 40);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `manufacturers`
--
ALTER TABLE `manufacturers`
  ADD PRIMARY KEY (`ID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
