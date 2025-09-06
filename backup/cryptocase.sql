-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1
-- Время создания: Сен 06 2025 г., 09:17
-- Версия сервера: 10.4.32-MariaDB
-- Версия PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `cryptocase`
--

-- --------------------------------------------------------

--
-- Структура таблицы `accounts_profile`
--

CREATE TABLE `accounts_profile` (
  `id` bigint(20) NOT NULL,
  `phone` varchar(32) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `balance_usd` decimal(14,2) NOT NULL,
  `deposit_total_usd` decimal(14,2) NOT NULL,
  `lost_total_usd` decimal(14,2) NOT NULL,
  `won_total_usd` decimal(14,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `accounts_profile`
--

INSERT INTO `accounts_profile` (`id`, `phone`, `created_at`, `updated_at`, `user_id`, `balance_usd`, `deposit_total_usd`, `lost_total_usd`, `won_total_usd`) VALUES
(2, '+79807508443', '2025-09-04 16:03:28.215476', '2025-09-04 16:03:28.215476', 2, 0.00, 0.00, 0.00, 0.00),
(3, '', '2025-09-04 16:05:06.531042', '2025-09-05 17:22:12.357155', 3, 995.00, 1000.00, 200.00, 195.00),
(4, '', '2025-09-05 15:46:11.875712', '2025-09-05 15:46:11.875712', 4, 0.00, 0.00, 0.00, 0.00),
(5, '', '2025-09-05 17:07:28.144781', '2025-09-05 17:07:28.144781', 5, 0.00, 0.00, 0.00, 0.00),
(6, '', '2025-09-05 17:09:02.866555', '2025-09-05 17:09:02.866555', 6, 0.00, 0.00, 0.00, 0.00),
(7, '', '2025-09-05 17:10:08.041037', '2025-09-05 17:10:08.041553', 7, 0.00, 0.00, 0.00, 0.00),
(8, '', '2025-09-05 17:11:44.217550', '2025-09-05 17:11:44.217550', 8, 0.00, 0.00, 0.00, 0.00);

-- --------------------------------------------------------

--
-- Структура таблицы `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add profile', 7, 'add_profile'),
(26, 'Can change profile', 7, 'change_profile'),
(27, 'Can delete profile', 7, 'delete_profile'),
(28, 'Can view profile', 7, 'view_profile'),
(29, 'Can add Крутка', 8, 'add_spin'),
(30, 'Can change Крутка', 8, 'change_spin'),
(31, 'Can delete Крутка', 8, 'delete_spin'),
(32, 'Can view Крутка', 8, 'view_spin'),
(33, 'Can add case', 9, 'add_case'),
(34, 'Can change case', 9, 'change_case'),
(35, 'Can delete case', 9, 'delete_case'),
(36, 'Can view case', 9, 'view_case'),
(37, 'Can add Тип кейса', 10, 'add_casetype'),
(38, 'Can change Тип кейса', 10, 'change_casetype'),
(39, 'Can delete Тип кейса', 10, 'delete_casetype'),
(40, 'Can view Тип кейса', 10, 'view_casetype'),
(41, 'Can add Приз кейса', 11, 'add_caseprize'),
(42, 'Can change Приз кейса', 11, 'change_caseprize'),
(43, 'Can delete Приз кейса', 11, 'delete_caseprize'),
(44, 'Can view Приз кейса', 11, 'view_caseprize'),
(45, 'Can add referral profile', 12, 'add_referralprofile'),
(46, 'Can change referral profile', 12, 'change_referralprofile'),
(47, 'Can delete referral profile', 12, 'delete_referralprofile'),
(48, 'Can view referral profile', 12, 'view_referralprofile'),
(49, 'Can add referral reward', 13, 'add_referralreward'),
(50, 'Can change referral reward', 13, 'change_referralreward'),
(51, 'Can delete referral reward', 13, 'delete_referralreward'),
(52, 'Can view referral reward', 13, 'view_referralreward');

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(2, 'pbkdf2_sha256$600000$QtcM1IH6M7LPx4YBscVI5K$sf4Td32Td+f86/PbhTXsG06YuXv4DnYkaPsQoxE7GzQ=', '2025-09-04 14:36:27.422740', 1, 'Angryfa', '', '', 'fa01_2001@mail.ru', 1, 1, '2025-09-04 14:36:00.164375'),
(3, 'pbkdf2_sha256$600000$nRAvSLbHQqwyliQuBcAiyf$ZtWObmh7N6ubKTGU3JFNq6QsPrXgRA22897T3WrzpOY=', NULL, 0, 'anton.fa01@mail.ru', '', '', 'anton.fa01@mail.ru', 0, 1, '2025-09-04 16:05:01.629037'),
(4, 'pbkdf2_sha256$600000$N0tisWUoFBjwRU9yVUk3A3$VRs8L7eRVSgK9ir1fxkK76Za4OiQZ8iCOwxxRzC8MJE=', NULL, 0, 'test@test.ru', '', '', 'test@test.ru', 0, 1, '2025-09-05 15:46:10.063653'),
(5, 'pbkdf2_sha256$600000$DtHgl7Nyb71gGfKmVNudCf$Wz2kqGMCg4rB2McDl3j4ODv2lqCfwFZNns3qRxYlN1M=', NULL, 0, 'angryfa@test.ru', '', '', 'angryfa@test.ru', 0, 1, '2025-09-05 17:04:18.168210'),
(6, 'pbkdf2_sha256$600000$lR2M7ALXpJlRg7M9ZJTjsW$d3tUo7OM1M885589ckoGnhYbVPbFGtGZRUDemYAaLjU=', NULL, 0, 'angryfa2@test.ru', '', '', 'angryfa2@test.ru', 0, 1, '2025-09-05 17:09:02.329313'),
(7, 'pbkdf2_sha256$600000$fNzJbyGFTbESHSe98bkyBy$fSedl9mNKTFtpFJAlKTG+65wKPMZ7amaTgRtLF3uJVk=', NULL, 0, 'angryfa3@test.ru', '', '', 'angryfa3@test.ru', 0, 1, '2025-09-05 17:10:07.207143'),
(8, 'pbkdf2_sha256$600000$m3eSdSZXl70LbusdhyHxLn$n/9N76lcHQIYk8RniJYLVYBBtgCKxGV3YUY1KEcIRRU=', NULL, 0, 'angryfa4@test.ru', '', '', 'angryfa4@test.ru', 0, 1, '2025-09-05 17:11:43.395291');

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `cases_case`
--

CREATE TABLE `cases_case` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `price_usd` decimal(10,2) NOT NULL,
  `spins_total` int(10) UNSIGNED NOT NULL CHECK (`spins_total` >= 0),
  `spins_used` int(10) UNSIGNED NOT NULL CHECK (`spins_used` >= 0),
  `is_active` tinyint(1) NOT NULL,
  `available_from` datetime(6) DEFAULT NULL,
  `available_to` datetime(6) DEFAULT NULL,
  `type_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cases_case`
--

INSERT INTO `cases_case` (`id`, `name`, `price_usd`, `spins_total`, `spins_used`, `is_active`, `available_from`, `available_to`, `type_id`) VALUES
(1, 'Starter Box', 5.00, 0, 0, 1, NULL, NULL, 1),
(2, 'Gold Rush Limited', 10.00, 500, 28, 1, NULL, NULL, 2),
(3, 'Happy Hour', 4.00, 0, 0, 1, '2025-09-04 15:25:00.000000', '2025-09-30 15:09:56.000000', 3),
(4, 'Anniversary Mega', 15.00, 100, 6, 1, '2025-09-04 15:26:17.000000', '2025-09-11 15:10:27.000000', 4);

-- --------------------------------------------------------

--
-- Структура таблицы `cases_caseprize`
--

CREATE TABLE `cases_caseprize` (
  `id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `amount_usd` decimal(14,2) NOT NULL,
  `weight` int(10) UNSIGNED NOT NULL CHECK (`weight` >= 0),
  `case_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cases_caseprize`
--

INSERT INTO `cases_caseprize` (`id`, `title`, `amount_usd`, `weight`, `case_id`) VALUES
(1, 'Small Reward', 1.00, 70, 1),
(2, 'Medium Reward', 3.00, 25, 1),
(3, 'Big Reward', 10.00, 5, 1),
(4, 'Gold Small', 5.00, 60, 2),
(5, 'Gold Medium', 15.00, 30, 2),
(6, 'Gold Big', 50.00, 10, 2),
(7, 'HH Small', 1.00, 50, 3),
(8, 'HH Medium', 3.00, 40, 3),
(9, 'HH Big', 20.00, 10, 3),
(10, 'A Small', 7.00, 60, 4),
(11, 'A Medium', 25.00, 30, 4),
(12, 'A Big', 100.00, 10, 4);

-- --------------------------------------------------------

--
-- Структура таблицы `cases_casetype`
--

CREATE TABLE `cases_casetype` (
  `id` bigint(20) NOT NULL,
  `type` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `is_limited` tinyint(1) NOT NULL,
  `is_timed` tinyint(1) NOT NULL,
  `sort_order` int(10) UNSIGNED NOT NULL CHECK (`sort_order` >= 0),
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cases_casetype`
--

INSERT INTO `cases_casetype` (`id`, `type`, `name`, `is_limited`, `is_timed`, `sort_order`, `is_active`) VALUES
(1, 'standard', 'Обычный', 0, 0, 10, 1),
(2, 'limited', 'Лимитированный', 1, 0, 20, 1),
(3, 'timed', 'По времени', 0, 1, 30, 1),
(4, 'limited_timed', 'Лимитированный + По времени', 1, 1, 40, 1);

-- --------------------------------------------------------

--
-- Структура таблицы `cases_spin`
--

CREATE TABLE `cases_spin` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `case_id` bigint(20) NOT NULL,
  `prize_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cases_spin`
--

INSERT INTO `cases_spin` (`id`, `created_at`, `case_id`, `prize_id`, `user_id`) VALUES
(18, '2025-09-04 16:06:29.779002', 1, 1, 3),
(19, '2025-09-04 16:13:23.821747', 1, 1, 3),
(20, '2025-09-04 16:13:25.702786', 1, 2, 3),
(21, '2025-09-04 16:13:27.416844', 1, 1, 3),
(22, '2025-09-04 16:13:28.897292', 1, 1, 3),
(23, '2025-09-04 16:13:30.322425', 1, 1, 3),
(24, '2025-09-04 16:13:31.341244', 1, 1, 3),
(25, '2025-09-04 16:13:32.217154', 1, 1, 3),
(26, '2025-09-04 16:13:33.327316', 2, 6, 3),
(27, '2025-09-04 16:38:14.214662', 2, 5, 3),
(28, '2025-09-04 16:45:39.349487', 1, 2, 3),
(29, '2025-09-04 16:45:41.430496', 1, 1, 3),
(30, '2025-09-04 16:45:43.305946', 1, 1, 3),
(31, '2025-09-04 16:45:43.971011', 1, 1, 3),
(32, '2025-09-04 16:45:44.495207', 1, 1, 3),
(33, '2025-09-04 16:45:45.451445', 1, 1, 3),
(34, '2025-09-04 16:45:46.405656', 1, 3, 3),
(35, '2025-09-04 16:45:47.181512', 1, 1, 3),
(36, '2025-09-04 16:45:47.933250', 1, 1, 3),
(37, '2025-09-04 16:45:48.619795', 1, 1, 3),
(38, '2025-09-04 16:45:49.217017', 1, 1, 3),
(39, '2025-09-04 16:45:50.218459', 2, 6, 3),
(40, '2025-09-04 16:45:51.898024', 3, 7, 3),
(41, '2025-09-04 16:45:53.123146', 4, 10, 3),
(42, '2025-09-04 16:45:54.387365', 2, 4, 3),
(43, '2025-09-04 16:45:55.152138', 2, 5, 3),
(44, '2025-09-04 16:45:56.396329', 2, 4, 3),
(45, '2025-09-04 16:45:57.249500', 2, 4, 3),
(46, '2025-09-04 16:45:58.300616', 2, 4, 3),
(47, '2025-09-04 16:45:59.026049', 2, 5, 3),
(48, '2025-09-04 16:46:01.204193', 2, 4, 3),
(49, '2025-09-04 16:46:02.757055', 1, 1, 3),
(50, '2025-09-04 16:46:03.822510', 2, 4, 3),
(51, '2025-09-04 16:46:04.802805', 2, 4, 3),
(52, '2025-09-04 16:46:05.697446', 2, 4, 3),
(53, '2025-09-04 16:46:06.502470', 2, 6, 3),
(54, '2025-09-05 15:14:48.147477', 2, 4, 3),
(55, '2025-09-05 15:14:50.467433', 3, 8, 3),
(56, '2025-09-05 15:14:52.350268', 4, 10, 3),
(57, '2025-09-05 15:14:55.472678', 1, 1, 3),
(58, '2025-09-05 15:14:57.163651', 2, 4, 3),
(59, '2025-09-05 15:14:58.972203', 3, 7, 3),
(60, '2025-09-05 15:15:00.639757', 4, 10, 3),
(61, '2025-09-05 15:15:02.359921', 2, 4, 3),
(62, '2025-09-05 15:15:03.925043', 2, 4, 3),
(63, '2025-09-05 15:15:04.857211', 2, 5, 3),
(64, '2025-09-05 15:15:05.618757', 2, 4, 3),
(65, '2025-09-05 15:15:06.262497', 2, 5, 3),
(66, '2025-09-05 15:15:07.648758', 2, 6, 3),
(67, '2025-09-05 17:21:47.197205', 1, 1, 3),
(68, '2025-09-05 17:22:02.864302', 1, 1, 3),
(69, '2025-09-05 17:22:04.907867', 2, 4, 3),
(70, '2025-09-05 17:22:06.843469', 2, 4, 3),
(71, '2025-09-05 17:22:08.568208', 2, 5, 3),
(72, '2025-09-05 17:22:10.601663', 2, 4, 3),
(73, '2025-09-05 17:22:12.357666', 2, 4, 3);

-- --------------------------------------------------------

--
-- Структура таблицы `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(26, '2025-09-04 15:10:03.562346', '3', 'Happy Hour', 1, '[{\"added\": {}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"HH Small ($1)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"HH Medium ($3)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"HH Big ($20)\"}}]', 9, 2),
(27, '2025-09-04 15:11:00.504663', '4', 'Anniversary Mega', 1, '[{\"added\": {}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"A Small ($7)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"A Medium ($25)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"A Big ($100)\"}}]', 9, 2),
(28, '2025-09-04 15:11:29.897871', '5', 'test', 1, '[{\"added\": {}}]', 9, 2),
(29, '2025-09-04 15:12:30.340836', '1', 'Starter Box', 2, '[]', 9, 2),
(30, '2025-09-04 15:12:37.130024', '5', 'test', 3, '', 9, 2),
(31, '2025-09-04 15:12:49.568909', '16', 'Spin #16 — Gold Rush Limited: $15.00', 3, '', 8, 2),
(32, '2025-09-04 15:12:49.571908', '15', 'Spin #15 — Anniversary Mega: $7.00', 3, '', 8, 2),
(33, '2025-09-04 15:12:49.574908', '14', 'Spin #14 — Anniversary Mega: $25.00', 3, '', 8, 2),
(34, '2025-09-04 15:17:09.890482', '3', 'Happy Hour', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(35, '2025-09-04 15:17:59.585363', '3', 'Happy Hour', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(36, '2025-09-04 15:23:20.965186', '3', 'Happy Hour', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(37, '2025-09-04 15:23:57.496588', '4', 'Anniversary Mega', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(38, '2025-09-04 15:24:17.817103', '4', 'Anniversary Mega', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(39, '2025-09-04 15:24:34.257659', '4', 'Anniversary Mega', 2, '[{\"changed\": {\"fields\": [\"Available from\"]}}]', 9, 2),
(40, '2025-09-04 15:24:54.658516', '17', 'Spin #17 — Anniversary Mega: $7.00', 3, '', 8, 2),
(41, '2025-09-04 15:45:59.310729', '1', 'Profile<Angryfa>', 2, '[{\"changed\": {\"fields\": [\"User\"]}}]', 7, 2),
(42, '2025-09-04 15:46:28.461973', '1', 'Profile<fa01_2001@mail.ru>', 2, '[{\"changed\": {\"fields\": [\"User\"]}}]', 7, 2),
(43, '2025-09-04 16:00:19.421415', '1', 'fa01_2001', 2, '[{\"changed\": {\"fields\": [\"Username\"]}}]', 4, 2),
(44, '2025-09-04 16:00:21.712195', '1', 'Profile<fa01_2001>', 2, '[]', 7, 2),
(45, '2025-09-04 16:03:28.218477', '2', 'Profile<Angryfa>', 1, '[{\"added\": {}}]', 7, 2),
(46, '2025-09-04 16:06:15.441005', '3', 'Profile<anton.fa01@mail.ru>', 2, '[{\"changed\": {\"fields\": [\"Balance usd\", \"Deposit total usd\"]}}]', 7, 2);

-- --------------------------------------------------------

--
-- Структура таблицы `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(7, 'accounts', 'profile'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(9, 'cases', 'case'),
(11, 'cases', 'caseprize'),
(10, 'cases', 'casetype'),
(8, 'cases', 'spin'),
(5, 'contenttypes', 'contenttype'),
(12, 'referrals', 'referralprofile'),
(13, 'referrals', 'referralreward'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Структура таблицы `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-09-03 15:16:18.889445'),
(2, 'auth', '0001_initial', '2025-09-03 15:16:19.357200'),
(3, 'admin', '0001_initial', '2025-09-03 15:16:19.501034'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-09-03 15:16:19.507033'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-09-03 15:16:19.513034'),
(6, 'contenttypes', '0002_remove_content_type_name', '2025-09-03 15:16:19.575478'),
(7, 'auth', '0002_alter_permission_name_max_length', '2025-09-03 15:16:19.625469'),
(8, 'auth', '0003_alter_user_email_max_length', '2025-09-03 15:16:19.636468'),
(9, 'auth', '0004_alter_user_username_opts', '2025-09-03 15:16:19.641468'),
(10, 'auth', '0005_alter_user_last_login_null', '2025-09-03 15:16:19.675911'),
(11, 'auth', '0006_require_contenttypes_0002', '2025-09-03 15:16:19.679911'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2025-09-03 15:16:19.685912'),
(13, 'auth', '0008_alter_user_username_max_length', '2025-09-03 15:16:19.695911'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2025-09-03 15:16:19.705911'),
(15, 'auth', '0010_alter_group_name_max_length', '2025-09-03 15:16:19.715910'),
(16, 'auth', '0011_update_proxy_permissions', '2025-09-03 15:16:19.721910'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2025-09-03 15:16:19.731641'),
(18, 'sessions', '0001_initial', '2025-09-03 15:16:19.760243'),
(19, 'accounts', '0001_initial', '2025-09-03 15:41:26.325611'),
(20, 'cases', '0001_initial', '2025-09-04 14:34:12.112025'),
(21, 'accounts', '0002_profile_balance_usd_profile_deposit_total_usd_and_more', '2025-09-04 15:43:58.129582'),
(22, 'cases', '0002_spin_user', '2025-09-04 15:43:58.189634'),
(24, 'referrals', '0001_initial', '2025-09-05 15:40:30.131349');

-- --------------------------------------------------------

--
-- Структура таблицы `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('37eb9a1b2p7gagv95hy8b08ui1cxhso4', '.eJxVjEEOwiAQRe_C2hCGMqW6dN8zkIEZpWpoUtqV8e7SpAvdvvf-f6tA25rDVmUJE6uLsur0yyKlp5Rd8IPKfdZpLusyRb0n-rBVjzPL63q0fweZam5r5zFacMgkiaMZEgoRRiDbEfr2cwbD0giyTz0AsO8i3Hp0jgcDpD5fAYk4Zg:1uuB4d:MgXqqOnpxEdnqeOPM2h3fekJnK81jLhQr0b64AVw6I0', '2025-09-18 14:36:27.426709');

-- --------------------------------------------------------

--
-- Структура таблицы `referrals_referralprofile`
--

CREATE TABLE `referrals_referralprofile` (
  `id` bigint(20) NOT NULL,
  `code` varchar(16) NOT NULL,
  `referred_at` datetime(6) DEFAULT NULL,
  `referred_by_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `referrals_referralprofile`
--

INSERT INTO `referrals_referralprofile` (`id`, `code`, `referred_at`, `referred_by_id`, `user_id`) VALUES
(1, 'M243TLCG', NULL, NULL, 4),
(2, 'XDNEEVB2', NULL, NULL, 3),
(3, 'TF3997E3', '2025-09-05 17:04:18.435035', 3, 5),
(4, 'Q2EXMKCK', '2025-09-05 17:09:02.589838', 5, 6),
(5, '9TL9JAQV', '2025-09-05 17:10:07.616575', 6, 7),
(6, 'F3WPJEV6', '2025-09-05 17:11:43.798410', 3, 8);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Индексы таблицы `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Индексы таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Индексы таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Индексы таблицы `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Индексы таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Индексы таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Индексы таблицы `cases_case`
--
ALTER TABLE `cases_case`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cases_case_type_id_ecc3407d_fk_cases_casetype_id` (`type_id`),
  ADD KEY `cases_case_available_from_937b91b1` (`available_from`),
  ADD KEY `cases_case_available_to_d63a5eeb` (`available_to`);

--
-- Индексы таблицы `cases_caseprize`
--
ALTER TABLE `cases_caseprize`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cases_caseprize_case_id_5ecb4fe9_fk_cases_case_id` (`case_id`);

--
-- Индексы таблицы `cases_casetype`
--
ALTER TABLE `cases_casetype`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type` (`type`);

--
-- Индексы таблицы `cases_spin`
--
ALTER TABLE `cases_spin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cases_spin_case_id_0bcf84d9_fk_cases_case_id` (`case_id`),
  ADD KEY `cases_spin_prize_id_43bb0dd8_fk_cases_caseprize_id` (`prize_id`),
  ADD KEY `cases_spin_user_id_e33108d3_fk_auth_user_id` (`user_id`);

--
-- Индексы таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Индексы таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Индексы таблицы `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Индексы таблицы `referrals_referralprofile`
--
ALTER TABLE `referrals_referralprofile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `referrals_referralpr_referred_by_id_d0360b18_fk_auth_user` (`referred_by_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT для таблицы `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT для таблицы `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT для таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `cases_case`
--
ALTER TABLE `cases_case`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT для таблицы `cases_caseprize`
--
ALTER TABLE `cases_caseprize`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT для таблицы `cases_casetype`
--
ALTER TABLE `cases_casetype`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT для таблицы `cases_spin`
--
ALTER TABLE `cases_spin`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT для таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT для таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT для таблицы `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT для таблицы `referrals_referralprofile`
--
ALTER TABLE `referrals_referralprofile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  ADD CONSTRAINT `accounts_profile_user_id_49a85d32_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `cases_case`
--
ALTER TABLE `cases_case`
  ADD CONSTRAINT `cases_case_type_id_ecc3407d_fk_cases_casetype_id` FOREIGN KEY (`type_id`) REFERENCES `cases_casetype` (`id`);

--
-- Ограничения внешнего ключа таблицы `cases_caseprize`
--
ALTER TABLE `cases_caseprize`
  ADD CONSTRAINT `cases_caseprize_case_id_5ecb4fe9_fk_cases_case_id` FOREIGN KEY (`case_id`) REFERENCES `cases_case` (`id`);

--
-- Ограничения внешнего ключа таблицы `cases_spin`
--
ALTER TABLE `cases_spin`
  ADD CONSTRAINT `cases_spin_case_id_0bcf84d9_fk_cases_case_id` FOREIGN KEY (`case_id`) REFERENCES `cases_case` (`id`),
  ADD CONSTRAINT `cases_spin_prize_id_43bb0dd8_fk_cases_caseprize_id` FOREIGN KEY (`prize_id`) REFERENCES `cases_caseprize` (`id`),
  ADD CONSTRAINT `cases_spin_user_id_e33108d3_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `referrals_referralprofile`
--
ALTER TABLE `referrals_referralprofile`
  ADD CONSTRAINT `referrals_referralpr_referred_by_id_d0360b18_fk_auth_user` FOREIGN KEY (`referred_by_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `referrals_referralprofile_user_id_00235b1a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
