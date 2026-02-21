-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Feb 21, 2026 at 12:05 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `shetimitra_ai`
--

-- --------------------------------------------------------

--
-- Table structure for table `crops`
--

CREATE TABLE `crops` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `crop_name` varchar(100) DEFAULT NULL,
  `sowing_date` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crops`
--

INSERT INTO `crops` (`id`, `user_id`, `crop_name`, `sowing_date`, `created_at`) VALUES
(12, 5, 'Cotton', '2026-02-21', '2026-02-19 16:11:03');

-- --------------------------------------------------------

--
-- Table structure for table `equipment`
--

CREATE TABLE `equipment` (
  `id` int(11) NOT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `type` enum('rent','sell') DEFAULT NULL,
  `price_per_day` int(11) DEFAULT NULL,
  `sell_price` int(11) DEFAULT NULL,
  `village` varchar(100) DEFAULT NULL,
  `contact` varchar(20) DEFAULT NULL,
  `photos` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `equipment`
--

INSERT INTO `equipment` (`id`, `owner_id`, `title`, `type`, `price_per_day`, `sell_price`, `village`, `contact`, `photos`) VALUES
(34, 2, 'seed machine', 'rent', 500, NULL, 'chopda', '9403514244', '[\"uploads/equipment\\\\seee1.jpg\", \"uploads/equipment\\\\see2.jpg\"]');

-- --------------------------------------------------------

--
-- Table structure for table `equipment_availability`
--

CREATE TABLE `equipment_availability` (
  `id` int(11) NOT NULL,
  `equipment_id` int(11) DEFAULT NULL,
  `available_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `equipment_booking`
--

CREATE TABLE `equipment_booking` (
  `id` int(11) NOT NULL,
  `equipment_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `customer_mobile` varchar(20) DEFAULT NULL,
  `customer_village` varchar(100) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `total_price` int(11) DEFAULT NULL,
  `payment_mode` varchar(20) DEFAULT NULL,
  `status` enum('pending','approved','completed','cancelled') DEFAULT 'pending',
  `owner_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `equipment_booking`
--

INSERT INTO `equipment_booking` (`id`, `equipment_id`, `user_id`, `customer_name`, `customer_mobile`, `customer_village`, `start_date`, `end_date`, `total_price`, `payment_mode`, `status`, `owner_id`) VALUES
(50, 34, 5, 'Kuldip Mahale', '09860107963', 'shahapur', '2026-02-20', '2026-02-24', 2500, 'upi', 'approved', 2);

-- --------------------------------------------------------

--
-- Table structure for table `equipment_photos`
--

CREATE TABLE `equipment_photos` (
  `id` int(11) NOT NULL,
  `equipment_id` int(11) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `equipment_rating`
--

CREATE TABLE `equipment_rating` (
  `id` int(11) NOT NULL,
  `equipment_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `review` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `mobile`, `password`) VALUES
(2, 'yash marathe', '9403514244', '12345'),
(5, 'Kuldip Kishor Mahale', '9890371852', '12345'),
(12, 'kishor waman patil', '8975337399', '#Kuldip2005');

-- --------------------------------------------------------

--
-- Table structure for table `wallet`
--

CREATE TABLE `wallet` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `type` enum('income','expense') DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wallet`
--

INSERT INTO `wallet` (`id`, `user_id`, `type`, `amount`, `description`, `created_at`) VALUES
(6, 2, 'income', 100000.00, 'cotton', '2026-02-19 06:56:23'),
(7, 2, 'expense', 20000.00, 'fertilizer', '2026-02-19 06:56:49'),
(8, 2, 'income', 1000.00, 'home', '2026-02-19 06:57:41'),
(10, 5, 'income', 750000.00, 'sale to maize', '2026-02-20 07:36:54'),
(11, 5, 'expense', 25000.00, 'all labours,equipments', '2026-02-20 07:37:43');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `crops`
--
ALTER TABLE `crops`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `equipment`
--
ALTER TABLE `equipment`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `equipment_availability`
--
ALTER TABLE `equipment_availability`
  ADD PRIMARY KEY (`id`),
  ADD KEY `equipment_id` (`equipment_id`);

--
-- Indexes for table `equipment_booking`
--
ALTER TABLE `equipment_booking`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `equipment_photos`
--
ALTER TABLE `equipment_photos`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `equipment_rating`
--
ALTER TABLE `equipment_rating`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mobile` (`mobile`);

--
-- Indexes for table `wallet`
--
ALTER TABLE `wallet`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `crops`
--
ALTER TABLE `crops`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `equipment`
--
ALTER TABLE `equipment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `equipment_availability`
--
ALTER TABLE `equipment_availability`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `equipment_booking`
--
ALTER TABLE `equipment_booking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT for table `equipment_photos`
--
ALTER TABLE `equipment_photos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `equipment_rating`
--
ALTER TABLE `equipment_rating`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `wallet`
--
ALTER TABLE `wallet`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `equipment_availability`
--
ALTER TABLE `equipment_availability`
  ADD CONSTRAINT `equipment_availability_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
