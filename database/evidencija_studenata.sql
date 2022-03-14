-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 14, 2022 at 10:49 AM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 8.0.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `evidencija_studenata`
--

-- --------------------------------------------------------

--
-- Table structure for table `korisnici`
--

CREATE TABLE `korisnici` (
  `id` int(11) NOT NULL,
  `ime` varchar(30) NOT NULL,
  `prezime` varchar(30) NOT NULL,
  `email` varchar(100) NOT NULL,
  `lozinka` varchar(120) NOT NULL,
  `rola` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `korisnici`
--

INSERT INTO `korisnici` (`id`, `ime`, `prezime`, `email`, `lozinka`, `rola`) VALUES
(10, 'admin', 'admin', 'admin@vtsnis.edu.rs', 'pbkdf2:sha256:260000$9PctCpeVY7JzTEvU$6badb10829d164510fb6568c93572dabd7bf20ebc563c6ef7a67536a573c8965', 'administrator'),
(27, 'Cile', 'Cilic', 'cc@vtsnis.edu.rs', 'pbkdf2:sha256:260000$PSth06fvI8lAy1m7$1c6299fc35987e2a44f856ea06dd09527df12f1c093c074c254b160c0d4cb99d', 'profesor'),
(28, 'Ema', 'Emic', 'ee@vtsnis.edu.rs', 'pbkdf2:sha256:260000$reBiwQPjiSdt9zng$5cdbd87c44c98b1419809afa38508d65a1fbdbb1d03aa88c35c75bd130ee6344', 'profesor'),
(30, 'Deki', 'Dekic', 'dd@vtsnis.edu.rs', 'pbkdf2:sha256:260000$0IqRApZ3m7t0zOJf$7103ac8e50d8d998f0cdffcb62e950fe5bf96e883011f75443ed0c626b159f90', 'profesor'),
(31, 'Goran', 'Gokic', 'gg@vtsnis.edu.rs', 'pbkdf2:sha256:260000$zP8lqhCyi9rtF8oR$b64b071762803b7a9cc4b20eb3d35f480423b679ba9ca1e41edd3a1510ede368', 'administrator'),
(32, 'Fiki', 'Fikic', 'ff@vtsnis.edu.rs', 'pbkdf2:sha256:260000$MPHcrkOZdryh0ScA$04918ae28f0c7828f7ae266b66b87a522f45d359cb21848a7eb0b3cc42024fa4', 'profesor'),
(42, 'profesor', 'profesor', 'profesor@vtsnis.edu.rs', 'pbkdf2:sha256:260000$awkz5CokA1ajYVnG$f1ce006ed075898257c5f16898a8da4c3873208bd625035b2c95c3af3a12e6f3', 'profesor'),
(47, 'Boki', 'Bokic', 'bb@vtsnis.edu.rs', 'pbkdf2:sha256:260000$UDEb1PpBt7tR4f3p$b7a8a05bbfec205f2267a7c36ea61f234795738abdc2d58a1874389afd94a23c', 'student'),
(48, 'Aca', 'Acic', 'aa@vtsnis.edu.rs', 'pbkdf2:sha256:260000$5FklYNmnuErtEKyV$48b8426c772c81cf6c4f9687a248a5b0531b7d2d3877a67a4bcaf05764e8b02c', 'student');

-- --------------------------------------------------------

--
-- Table structure for table `ocene`
--

CREATE TABLE `ocene` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `predmet_id` int(11) NOT NULL,
  `ocena` smallint(6) NOT NULL,
  `datum` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `ocene`
--

INSERT INTO `ocene` (`id`, `student_id`, `predmet_id`, `ocena`, `datum`) VALUES
(55, 44, 3, 10, '2022-02-16'),
(56, 44, 5, 8, '2022-02-16'),
(57, 44, 8, 10, '2022-02-16'),
(58, 44, 9, 9, '2022-02-16'),
(59, 44, 6, 10, '2022-02-16'),
(60, 44, 10, 10, '2022-02-16');

-- --------------------------------------------------------

--
-- Table structure for table `predmeti`
--

CREATE TABLE `predmeti` (
  `id` int(11) NOT NULL,
  `sifra` varchar(30) NOT NULL,
  `naziv` varchar(100) CHARACTER SET utf8 NOT NULL,
  `godina_studija` smallint(6) NOT NULL,
  `espb` int(11) NOT NULL,
  `obavezni_izborni` varchar(10) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `predmeti`
--

INSERT INTO `predmeti` (`id`, `sifra`, `naziv`, `godina_studija`, `espb`, `obavezni_izborni`) VALUES
(3, '111', 'matematika', 1, 6, 'izborni'),
(5, '222', 'Fizika', 1, 8, 'izborni'),
(6, '333', 'Elektronika', 3, 6, 'izborni'),
(7, '444', 'Operativni sistemi', 2, 8, 'obavezni'),
(8, '555', 'Algoritmi i strukture podataka', 1, 6, 'obavezni'),
(9, '666', 'Baze Podataka', 2, 6, 'obavezni'),
(10, '777', 'Administriranje racunarskih mreza', 2, 6, 'izborni');

-- --------------------------------------------------------

--
-- Table structure for table `studenti`
--

CREATE TABLE `studenti` (
  `id` int(11) NOT NULL,
  `ime` varchar(30) CHARACTER SET utf8 NOT NULL,
  `ime_roditelja` varchar(30) NOT NULL,
  `prezime` varchar(30) NOT NULL,
  `broj_indeksa` varchar(10) CHARACTER SET utf8 NOT NULL,
  `godina_studija` smallint(6) NOT NULL,
  `jmbg` bigint(20) NOT NULL,
  `datum_rodjenja` date NOT NULL,
  `espb` int(11) NOT NULL,
  `prosek_ocena` float NOT NULL,
  `broj_telefona` varchar(20) CHARACTER SET utf8 NOT NULL,
  `email` varchar(100) NOT NULL,
  `slika` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `studenti`
--

INSERT INTO `studenti` (`id`, `ime`, `ime_roditelja`, `prezime`, `broj_indeksa`, `godina_studija`, `jmbg`, `datum_rodjenja`, `espb`, `prosek_ocena`, `broj_telefona`, `email`, `slika`) VALUES
(44, 'Boki', 'Bob', 'Bokic', 'rer1/22', 1, 123456789, '2022-02-16', 38, 9.5, '123456', 'bb@vtsnis.edu.rs', ''),
(45, 'Aca', 'Akili', 'Acic', 'rer2/22', 1, 123456789, '2022-02-16', 0, 0, '123456', 'aa@vtsnis.edu.rs', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `korisnici`
--
ALTER TABLE `korisnici`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ocene`
--
ALTER TABLE `ocene`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ocene_predmet` (`predmet_id`),
  ADD KEY `ocene_student` (`student_id`);

--
-- Indexes for table `predmeti`
--
ALTER TABLE `predmeti`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `studenti`
--
ALTER TABLE `studenti`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `korisnici`
--
ALTER TABLE `korisnici`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `ocene`
--
ALTER TABLE `ocene`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- AUTO_INCREMENT for table `predmeti`
--
ALTER TABLE `predmeti`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `studenti`
--
ALTER TABLE `studenti`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ocene`
--
ALTER TABLE `ocene`
  ADD CONSTRAINT `ocene_predmet` FOREIGN KEY (`predmet_id`) REFERENCES `predmeti` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `ocene_student` FOREIGN KEY (`student_id`) REFERENCES `studenti` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
