-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1
-- Время создания: Сен 20 2025 г., 22:20
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
-- Структура таблицы `accounts_deposit`
--

CREATE TABLE `accounts_deposit` (
  `id` bigint(20) NOT NULL,
  `amount_usd` decimal(14,2) NOT NULL,
  `method` varchar(50) NOT NULL,
  `details` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `comment` longtext NOT NULL,
  `status_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `accounts_deposit`
--

INSERT INTO `accounts_deposit` (`id`, `amount_usd`, `method`, `details`, `created_at`, `processed_at`, `comment`, `status_id`, `user_id`) VALUES
(1, 50.00, 'USDT', 'test', '2025-09-10 16:53:31.273239', '2025-09-10 16:53:44.825412', '', 2, 2),
(2, 100.00, 'USDT', 'test', '2025-09-10 17:32:00.360532', '2025-09-10 17:32:04.705590', '', 2, 2);

-- --------------------------------------------------------

--
-- Структура таблицы `accounts_depositstatus`
--

CREATE TABLE `accounts_depositstatus` (
  `id` bigint(20) NOT NULL,
  `code` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `accounts_depositstatus`
--

INSERT INTO `accounts_depositstatus` (`id`, `code`, `name`) VALUES
(1, 'pending', 'В ожидании'),
(2, 'approved', 'Подтверждено'),
(3, 'rejected', 'Отклонено'),
(4, 'cancelled', 'Отменено');

-- --------------------------------------------------------

--
-- Структура таблицы `accounts_profile`
--

CREATE TABLE `accounts_profile` (
  `id` bigint(20) NOT NULL,
  `phone` varchar(32) NOT NULL,
  `balance_usd` decimal(14,2) NOT NULL,
  `deposit_total_usd` decimal(14,2) NOT NULL,
  `won_total_usd` decimal(14,2) NOT NULL,
  `lost_total_usd` decimal(14,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `client_seed` varchar(64) DEFAULT NULL,
  `pf_nonce` int(10) UNSIGNED NOT NULL CHECK (`pf_nonce` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `accounts_profile`
--

INSERT INTO `accounts_profile` (`id`, `phone`, `balance_usd`, `deposit_total_usd`, `won_total_usd`, `lost_total_usd`, `created_at`, `updated_at`, `user_id`, `client_seed`, `pf_nonce`) VALUES
(1, '', 116.00, 0.00, 5.00, 114.00, '2025-09-08 11:40:43.254665', '2025-09-20 20:15:49.989162', 2, '69efda1409a522185d41fb9d7f2a5560', 34),
(2, '', 0.00, 0.00, 0.00, 0.00, '2025-09-20 18:22:36.013318', '2025-09-20 18:22:36.013318', 1, '17d053fcb6af0b4153ba2298b8343d30', 0);

-- --------------------------------------------------------

--
-- Структура таблицы `accounts_withdrawal`
--

CREATE TABLE `accounts_withdrawal` (
  `id` bigint(20) NOT NULL,
  `amount_usd` decimal(14,2) NOT NULL,
  `method` varchar(50) NOT NULL,
  `details` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `comment` longtext NOT NULL,
  `status_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `accounts_withdrawalstatus`
--

CREATE TABLE `accounts_withdrawalstatus` (
  `id` bigint(20) NOT NULL,
  `code` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `accounts_withdrawalstatus`
--

INSERT INTO `accounts_withdrawalstatus` (`id`, `code`, `name`) VALUES
(1, 'pending', 'В ожидании'),
(2, 'approved', 'Подтверждено'),
(3, 'rejected', 'Отклонено'),
(4, 'cancelled', 'Отменено');

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
(25, 'Can add Статус депозита', 7, 'add_depositstatus'),
(26, 'Can change Статус депозита', 7, 'change_depositstatus'),
(27, 'Can delete Статус депозита', 7, 'delete_depositstatus'),
(28, 'Can view Статус депозита', 7, 'view_depositstatus'),
(29, 'Can add Статус вывода', 8, 'add_withdrawalstatus'),
(30, 'Can change Статус вывода', 8, 'change_withdrawalstatus'),
(31, 'Can delete Статус вывода', 8, 'delete_withdrawalstatus'),
(32, 'Can view Статус вывода', 8, 'view_withdrawalstatus'),
(33, 'Can add withdrawal', 9, 'add_withdrawal'),
(34, 'Can change withdrawal', 9, 'change_withdrawal'),
(35, 'Can delete withdrawal', 9, 'delete_withdrawal'),
(36, 'Can view withdrawal', 9, 'view_withdrawal'),
(37, 'Can add profile', 10, 'add_profile'),
(38, 'Can change profile', 10, 'change_profile'),
(39, 'Can delete profile', 10, 'delete_profile'),
(40, 'Can view profile', 10, 'view_profile'),
(41, 'Can add deposit', 11, 'add_deposit'),
(42, 'Can change deposit', 11, 'change_deposit'),
(43, 'Can delete deposit', 11, 'delete_deposit'),
(44, 'Can view deposit', 11, 'view_deposit'),
(45, 'Can add case', 12, 'add_case'),
(46, 'Can change case', 12, 'change_case'),
(47, 'Can delete case', 12, 'delete_case'),
(48, 'Can view case', 12, 'view_case'),
(49, 'Can add Приз кейса', 13, 'add_caseprize'),
(50, 'Can change Приз кейса', 13, 'change_caseprize'),
(51, 'Can delete Приз кейса', 13, 'delete_caseprize'),
(52, 'Can view Приз кейса', 13, 'view_caseprize'),
(53, 'Can add Тип кейса', 14, 'add_casetype'),
(54, 'Can change Тип кейса', 14, 'change_casetype'),
(55, 'Can delete Тип кейса', 14, 'delete_casetype'),
(56, 'Can view Тип кейса', 14, 'view_casetype'),
(57, 'Can add Крутка', 15, 'add_spin'),
(58, 'Can change Крутка', 15, 'change_spin'),
(59, 'Can delete Крутка', 15, 'delete_spin'),
(60, 'Can view Крутка', 15, 'view_spin'),
(61, 'Can add Процент рефералов (уровень)', 16, 'add_referrallevelconfig'),
(62, 'Can change Процент рефералов (уровень)', 16, 'change_referrallevelconfig'),
(63, 'Can delete Процент рефералов (уровень)', 16, 'delete_referrallevelconfig'),
(64, 'Can view Процент рефералов (уровень)', 16, 'view_referrallevelconfig'),
(65, 'Can add referral profile', 17, 'add_referralprofile'),
(66, 'Can change referral profile', 17, 'change_referralprofile'),
(67, 'Can delete referral profile', 17, 'delete_referralprofile'),
(68, 'Can view referral profile', 17, 'view_referralprofile'),
(69, 'Can add ticket', 18, 'add_ticket'),
(70, 'Can change ticket', 18, 'change_ticket'),
(71, 'Can delete ticket', 18, 'delete_ticket'),
(72, 'Can view ticket', 18, 'view_ticket'),
(73, 'Can add ticket message', 19, 'add_ticketmessage'),
(74, 'Can change ticket message', 19, 'change_ticketmessage'),
(75, 'Can delete ticket message', 19, 'delete_ticketmessage'),
(76, 'Can view ticket message', 19, 'view_ticketmessage'),
(77, 'Can add Настройки кэшбэка', 20, 'add_cashbacksettings'),
(78, 'Can change Настройки кэшбэка', 20, 'change_cashbacksettings'),
(79, 'Can delete Настройки кэшбэка', 20, 'delete_cashbacksettings'),
(80, 'Can view Настройки кэшбэка', 20, 'view_cashbacksettings'),
(81, 'Can add Начисление кэшбэка', 21, 'add_cashbackaccrual'),
(82, 'Can change Начисление кэшбэка', 21, 'change_cashbackaccrual'),
(83, 'Can delete Начисление кэшбэка', 21, 'delete_cashbackaccrual'),
(84, 'Can view Начисление кэшбэка', 21, 'view_cashbackaccrual'),
(85, 'Can add Списание кэшбэка', 22, 'add_cashbackdebit'),
(86, 'Can change Списание кэшбэка', 22, 'change_cashbackdebit'),
(87, 'Can delete Списание кэшбэка', 22, 'delete_cashbackdebit'),
(88, 'Can view Списание кэшбэка', 22, 'view_cashbackdebit');

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
(1, 'pbkdf2_sha256$600000$FJw3NwDD2VqcLUMG2ARNdu$BSOoytCaRkFkGIxCTZigC7N673qvIUjwmhuO8fOyd1k=', '2025-09-08 11:21:15.128715', 1, 'fa01_2001@mail.ru', '', '', '', 1, 1, '2025-09-08 11:21:01.677682'),
(2, 'pbkdf2_sha256$600000$UKd4NG2yMAeVBHOMguomKz$/XpYZ4634lH2b5k9A4UJlPrEytM+KrWbh46UbDny+Lk=', NULL, 0, 'anton.fa01@mail.ru', '', '', 'anton.fa01@mail.ru', 0, 1, '2025-09-08 11:40:42.704973');

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
(1, 'Starter Box', 5.00, 0, 0, 1, NULL, NULL, 1);

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
(3, 'Big Reward', 10.00, 5, 1);

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
(1, 'standard', 'Обычный', 0, 0, 10, 1);

-- --------------------------------------------------------

--
-- Структура таблицы `cases_spin`
--

CREATE TABLE `cases_spin` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `case_id` bigint(20) NOT NULL,
  `prize_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `client_seed` varchar(64) DEFAULT NULL,
  `nonce` int(10) UNSIGNED DEFAULT NULL CHECK (`nonce` >= 0),
  `rng_value` decimal(20,18) DEFAULT NULL,
  `roll_digest` varchar(64) DEFAULT NULL,
  `server_seed` longtext DEFAULT NULL,
  `server_seed_hash` varchar(64) DEFAULT NULL,
  `weights_snapshot` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`weights_snapshot`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cases_spin`
--

INSERT INTO `cases_spin` (`id`, `created_at`, `case_id`, `prize_id`, `user_id`, `client_seed`, `nonce`, `rng_value`, `roll_digest`, `server_seed`, `server_seed_hash`, `weights_snapshot`) VALUES
(1, '2025-09-10 17:31:28.832085', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 1, 0.540959409773480226, '8a7c50dd70c89a7b8f40fbd33aee257b8fa6931672d6577ec109826b4b350dbf', 'sUtc/RjLbVmbwazcO+xRgekpoONdEY6+I5FBVFLHtoU=', 'd9103224e87b42f77db07c4ced2e6a813a7645d5f558c9b6db3aa9c7ce610cb3', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(2, '2025-09-10 17:31:31.109289', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 2, 0.935623972777340329, 'ef850d7c6ea9559d62b0ea78a972421cfbc053c85f3f0ecbf0c4fc6fcf6ffd2f', 'RuRK8WNi67eHARUzGT4nGSvqy7I19+k5W9xiwOmRLPA=', '616e2352232dae616c893c36e15675dab6536051a193c01c398bea0116897057', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(3, '2025-09-10 17:31:32.960015', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 3, 0.073818854403684853, '12e5cadd7df48291a621d4aa4f5f72b261934a589b1cc2df2e336f5c9bbe9a41', 'AZxV8mfjkF3Sd+s/c+DL8vVw+DjB6ZN6uQeeN3jH4lA=', 'f5804211bb1dd37c426affa65e719d2ba70aab921ee228700ffbe9800ad751a5', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(4, '2025-09-10 17:31:34.218667', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 4, 0.287748811220573941, '49a9e7f5a7be00cfe85fd14768269a536e22f031f3a4f357ad0f791e04da4c8f', 'cXN+YIn9akO1luzFNJWrxOyPH+zxPqTz1nEiuC+hPSg=', '9a017eab275b0b144af930bf5f30a13f1de8a01b1168d490c73689c56ab40238', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(5, '2025-09-10 17:31:35.081310', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 5, 0.918124260278208038, 'eb0a31078f20e456ac7014684b24f1185727f9da091349200e1e3cc6ad64e12c', 'ax+8wDgMPuYps0ZDSfdVimVtowcxhycUYmY0f/uPJTI=', 'd17524a0c25876ab164a348bc1419298b7732ec90fdcad402faec15d80ea094c', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(6, '2025-09-10 17:31:35.693421', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 6, 0.927259480773789946, 'ed60e098d4518274bb225dff542d2c8c54ee298432b52051619c5f26e74ff3b7', 'XFbL3B8lGQx284Olzgo+wGLG0taYJm5kmvqt44z1ECQ=', 'fcd5e170dc9528471bc5067a63b918bce779e75cda5d6c68c59de8e113bed396', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(7, '2025-09-10 17:31:37.113289', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 7, 0.402973422327276509, '672944260d8789d6ac0fa008cb7d711df5d76c29318b043d2996c1e90e1164e3', 'PGwPk1WJh5D1FXMsCuewVCKNRghjTDZMmWEtSh8f28E=', '757c5f4c75bda1bab4843553469a89cca668500b1f373346170270b2ae36d6d7', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(8, '2025-09-10 17:31:38.482196', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 8, 0.631013810006057607, 'a18a1efd4ce565fe4fe05a8bc30927541775d22702a95bb2a8cbebb22cb2cd63', '+gBwhLYiK7GJfgSNEc5s6AckJcLeyx4fuDh2NXYcTOk=', '4b0484d20216c1e1129bdbdbc7eb21c22a0d2b1e8448920e0e4b3b474c06a9b3', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(9, '2025-09-10 17:31:39.460107', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 9, 0.742512473044554477, 'be154c2499339126e8c87ea097f46322843aab2692800e193ce174f725ace08d', 'm9c+ipR2TVxDDB7idfzQbacmm7WXT6Pwy2MxkjSGNIg=', 'b5af2abea58418100c5c1ea2c282c600b2a3451ef87ef479adcf046c230babab', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(10, '2025-09-10 17:31:40.365180', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 10, 0.762312590540220825, 'c326eafdb30488ece3157419e6966f5f88f7d5b739c36db1c1b2c4459cd2989e', 'IiIrHMWFohTJ9gWbFCGAtv2rHBhObnG0w/lUBoUvbIY=', '0d9f881a5f32f8780ebd94d0548ee0e9673f53a777493c062e9d56cd82bcbdd8', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(11, '2025-09-10 17:31:41.160216', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 11, 0.206474795540106948, '34db883e4b051a8a46dacb93433c6d36d3952fd1a943398b22868b74fb3e4f6e', 'iMN3ZtAYlG5g/n1tlMx3ueJhcUXRWOSZ1bLVbinVL5Y=', 'a252d3bdcf0c065b4028f8828e641bc47171940a34daeed136f505c1fdef02c3', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(12, '2025-09-10 17:31:42.072060', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 12, 0.428004651238810929, '6d91b67b9b48c5649fa1415c44ffb0ebb8f92ab36c38678748dec1821b4b36b8', '6tAlMfdSQ3K6JVk+Q/dIHf4acLDTc/H7C/XtXPR5pS8=', 'a7430b0a9340fc8030ac89c9df0f22e08f74d5c2efd1f9ff8d684b5046a1f8bd', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(13, '2025-09-10 17:31:42.813337', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 13, 0.324889490722141572, '532bf5297737b61e1f70e6204e1c2afa8696f309fe0d4794f47d1d1881706d6a', 'd6A7vtH7SWMijzrdJVFPUEzBjNXKdgUpeXs/VPiUMUo=', '963185c4b8b1f6ffdded28e2f023f6b8a876d164d82f520d2ad317d3d1f60048', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(14, '2025-09-10 17:31:43.939769', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 14, 0.045651196730594812, '0bafcbfcfb2dc2e4a1aa32a6d665b280e4f813939a97246de266a2a62e1279bb', 'zG4h4BnkyvAx9WIW+Z70xpPZUm4AySVVN75f2KK2H3s=', 'cd600c2bbed816d9a043feac36101f6873e17db7d6e3068b72593b35a06a3787', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(15, '2025-09-10 17:32:08.557031', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 15, 0.676344091260920210, 'ad24e2e8cef95c23de6538784521906b05cfb79d4d9fd8415909cc8c48c864a3', 'TNO8PUUiv2sHvGXx/jtsOJKMHUPPiH4EuLy8J/RwF8M=', '8e3ec278ccf8add039e48af0609572aa93864597b2bd6c448a29ea5624d2538c', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(16, '2025-09-10 17:32:10.650411', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 16, 0.314718302858617349, '509160f23afa8c5aa7d1dce555297405b80a9c52f817ce8a1caf3a116279c432', 'IX0s5WPwo3ZsusnvcTilhmpQr4adqUaJ/4LBcKC9WEA=', '76ab5cb14be1e26af6d43e786a302342fe116d58560436a95880113092af4c7f', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(17, '2025-09-10 17:32:11.404704', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 17, 0.435371443118309331, '6f7480bdce32d792c86b769f0339660372efd341e7d0f782fb12b4146c8cb762', 'wMnCCpfwU2JPy74CWmPBjneAzczVaaZ/2iG1+LhapLw=', 'a333fb9a9ce0109e947144652e622106d71336c856a9f7be8e941390449a89b7', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(18, '2025-09-10 17:32:12.134126', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 18, 0.569118403755034974, '91b1be63adfa3bf1600b9d9f0d875280ff082c1bace346b3db6fbd07b573e9ab', 'Ot8A8yIuJW5cNYSdTFPUnzcHrfKVrIKm2AL1EhGGf/0=', '3c6a046d168939c5a75f8ea5077c5eb8dbb6c8cebaf14779bd26bfb4678eca0d', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(19, '2025-09-10 17:34:45.742211', 1, 3, 2, '69efda1409a522185d41fb9d7f2a5560', 19, 0.951704085752117512, 'f3a2e103c6617b37b0ca0aafab0a33da60a2023ff12ba6990b37f7b945c49385', 'IZub3x+ACaGhkvLiKASsjUhDBsRbGUJPBBmf0DPBGk4=', '0c1d3ca0429357fd9768a011086bdb28748dc18cbb26c866e97961c3a9dfa7d7', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(20, '2025-09-10 17:50:10.316785', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 20, 0.006101965207298221, '018fe5fd01b588a30caf8529c920e26a5c199e815f39d8326ecc68b61196dd7b', 'dg3X4IM5vYnWRKDco/SCFUDIaBCPk7SbwKw6FskDHlc=', '2c2061bfc9a93f94a15b5b194c633fb9464bc3c88587bfac0293efaec51890bf', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(21, '2025-09-10 17:51:51.627814', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 21, 0.416426653287922832, '6a9aefe90dea83a6f82ddf46a909a546df37a7a246e4c979c393f91fa455497a', 'qswu7Skgn9qB/Sj7iSzU1Wo3qJe4W7bOnHfBfFfFGeQ=', 'b68498e10ff6557aa9ced18cc6bc8f0006e28a4f6cb5fab546a45344a3a70469', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(22, '2025-09-10 18:00:54.686375', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 22, 0.586588929928988367, '962ab12e3d9aada7feb16f14d74699c05402d2b9872178809fe90cbb8c032eb2', 'J7Utc+Y8StJyazPq7e3QmDTALDCdAc3Iwp6pfHjLLiE=', '8ae483a725760e7982fdf6bb98a13fe3ddd3f55d6e1548c5bc9942788bcfd543', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(23, '2025-09-10 18:01:02.245544', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 23, 0.708735655546942844, 'b56fb32e154f4ce3b7c698ff899fd21579fd9bc9af97e19024a457b81173bbeb', 'KzKpeU9APCJWrn9F8jqoEQnleWkhQ5rvGH2897XeoLw=', '4a3a6f70751500945b227bccf8a16d22c7b4698f3c05662183f32a31ed3e73ce', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(24, '2025-09-10 18:01:12.337030', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 24, 0.289688671465863301, '4a290969f7b2c918af8aa86df68626f89a0b0bcd56545fcff14b3ac4c99602ce', 'Qu0UUim0k7Z41FBJGj1hkRJ6txHktlKgFhQLi54IaCc=', '4639fd0edf2517d3b35353bb13ff2ba27c85efb63b2fe2ae7638fce6a29df5ee', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(25, '2025-09-10 18:03:01.213503', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 25, 0.666286040997335238, 'aa91b8d3dd6827294fb43f56aa3170d8aa0f46c9eabc9a0b469c34e6c8d40988', 'E0Xl5dxiSpAINZxhJzZ8dbDjMSsrRFVpKBznJBhY7a0=', 'f4bf53df1ea02e67d2fc090ae783eedf31417d89de0ab97bc45445bff9edbcab', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(26, '2025-09-10 18:03:04.871429', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 26, 0.450834180655649730, '7369de6dd5c0b64263fbbfa589950b93937df125d27d20ee2b61347e64a0d533', 'EejcWGPVmBxe0bqSQlq1xkUe167MBOamXepWzRt0qWA=', '37ce5b743ee2c794e596c644ec0f09711a721700f7136ef7149a86cb03a42bac', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(27, '2025-09-10 18:03:12.714050', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 27, 0.401459905631078140, '66c6138d5739ea8d310b7d93c51a6a11a32de0637deb4d51af963fa14f67c996', 'wvwJkQ07o3rQAWjudhx3hD/3a0jXJda/C+0XM7bKouU=', '2683991db58d0b34a0a083bec996379783d368c0c76a8cacc23e229e1a13145b', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(28, '2025-09-10 18:03:18.864622', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 28, 0.357801003801767159, '5b98d8b9cdf7c77a73c0f8c5dae0e3ccf1c666d0567b978c8cb7682ba478f180', 'AzZhcAQP+9ynSvDaTp/x645Uofarj6d86adBRM28L+Y=', '6d3900215da3b5ade45076f25a18c143162a143b0e88d9aef1f78431c01ae1e0', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(29, '2025-09-10 18:03:23.707051', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 29, 0.098282097790301615, '192903fbcaa794f1d8d39ef369e182aabd771d1b17f59670c283712ea1cb23af', 'VIQ0ZdZdFJJyBjqERwzKtFB0KE0B94pefp4Uut+7WZg=', '1b800c9b05087807092b1242983b872ddfb10f38ead6b829bcaf25f702cca7ff', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(30, '2025-09-10 18:03:26.676410', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 30, 0.012569674034184963, '0337c422e5f0ceade87c3d2c11e784e321f1031886c86aab362f9598fb3357fd', 'AG86V3Rdd4K9jywRY2NbPoYK3WREMuokIqrvHAV+9ck=', '6d136ffaa51dbc0608ffb1fc6bfcadffe7adbb15e5fed266027d97ec5f66253f', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(31, '2025-09-10 18:03:29.186592', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 31, 0.771433075952814074, 'c57ca358452013cc8f99b6b45e3bc72f0c21483033f791c92c55294b9e8c76d2', 'h/7ea7uAsxHP5S8R25GuAJCqIgrVldYJpWCgG2c+vBY=', '0fe70ce13d3af35df649d5ebee14ce400a5a41a1eeb1024650b9b15d619e8831', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(32, '2025-09-11 16:01:10.645701', 1, 1, 2, '69efda1409a522185d41fb9d7f2a5560', 32, 0.482298759040884484, '7b77ee74fb634b5903cb37ff38db7bcb8a799cae66cf656c8f04681ac7d7fe12', 'dvzJjKZ1ZxAF2oLZcqbhRr2XlT5okZtp9Gp5FmNUqjg=', '0786047c7f48975e6ff1176707fbef27d19834dc75bb22169d660372aa6a15ed', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(33, '2025-09-20 19:57:22.691986', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 33, 0.711452711427319029, 'b621c3d03b19bee157b62124bcedfaa9bb73a946dc55bd0456efb2b2365f90a3', 'yzfswE908sp+EAvY7Q/IrvuJHl8cxT7M6wgfHCf/xTE=', '700384a11b7e831a0d70a5da326ad71947e143a4340a599d42b57461963d83d9', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]'),
(34, '2025-09-20 20:15:49.989162', 1, 2, 2, '69efda1409a522185d41fb9d7f2a5560', 34, 0.917383310709675825, 'ead9a1f564ee8f275201222015048ccd380bd89426d2d7785dcb77c7164e39c3', 'zFDjXluP9YZdvT3gVhaYcAuxPQ53gM04Jvj9SKX3Exs=', '6cf4c92539bb85ce3f2bdd6dadd75ee856e029a9602577820b5b63a945e88767', '[{\"prize_id\": 1, \"weight\": 70, \"amount_usd\": \"1.00\"}, {\"prize_id\": 2, \"weight\": 25, \"amount_usd\": \"3.00\"}, {\"prize_id\": 3, \"weight\": 5, \"amount_usd\": \"10.00\"}]');

-- --------------------------------------------------------

--
-- Структура таблицы `cashback_cashbackaccrual`
--

CREATE TABLE `cashback_cashbackaccrual` (
  `id` bigint(20) NOT NULL,
  `amount_usd` decimal(16,2) NOT NULL,
  `base_deposits_usd` decimal(16,2) NOT NULL,
  `base_withdrawals_usd` decimal(16,2) NOT NULL,
  `base_net_usd` decimal(16,2) NOT NULL,
  `percent_used` decimal(6,2) NOT NULL,
  `slot_started_at` datetime(6) NOT NULL,
  `computed_at` datetime(6) NOT NULL,
  `status` varchar(16) NOT NULL,
  `note` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cashback_cashbackaccrual`
--

INSERT INTO `cashback_cashbackaccrual` (`id`, `amount_usd`, `base_deposits_usd`, `base_withdrawals_usd`, `base_net_usd`, `percent_used`, `slot_started_at`, `computed_at`, `status`, `note`, `user_id`) VALUES
(1, 15.00, 150.00, 0.00, 150.00, 10.00, '2025-09-13 16:00:00.000000', '2025-09-13 16:27:19.367747', 'calculated', '', 2),
(2, 15.00, 150.00, 0.00, 150.00, 10.00, '2025-09-13 17:16:44.299421', '2025-09-13 17:16:44.303422', 'calculated', '', 2),
(3, 15.00, 150.00, 0.00, 150.00, 10.00, '2025-09-13 18:07:00.630655', '2025-09-13 18:07:00.634655', 'calculated', '', 2),
(4, 15.00, 150.00, 0.00, 150.00, 10.00, '2025-09-13 19:16:11.070120', '2025-09-13 19:16:11.076121', 'calculated', '', 2),
(5, 15.00, 150.00, 0.00, 150.00, 10.00, '2025-09-20 20:14:47.330737', '2025-09-20 20:14:47.337665', 'calculated', '', 2);

-- --------------------------------------------------------

--
-- Структура таблицы `cashback_cashbackdebit`
--

CREATE TABLE `cashback_cashbackdebit` (
  `id` bigint(20) NOT NULL,
  `amount_usd` decimal(16,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `status` varchar(16) NOT NULL,
  `note` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cashback_cashbackdebit`
--

INSERT INTO `cashback_cashbackdebit` (`id`, `amount_usd`, `created_at`, `status`, `note`, `user_id`) VALUES
(1, 15.00, '2025-09-13 16:54:02.062425', 'completed', 'Перевод с кэшбэка на баланс', 2),
(2, 15.00, '2025-09-13 17:19:19.060338', 'completed', 'Перевод с кэшбэка на баланс', 2),
(3, 15.00, '2025-09-13 18:07:06.074731', 'completed', 'Перевод с кэшбэка на баланс', 2),
(4, 15.00, '2025-09-13 19:16:27.016546', 'completed', 'Перевод с кэшбэка на баланс', 2),
(5, 15.00, '2025-09-20 20:15:43.926354', 'completed', 'Перевод с кэшбэка на баланс', 2);

-- --------------------------------------------------------

--
-- Структура таблицы `cashback_cashbacksettings`
--

CREATE TABLE `cashback_cashbacksettings` (
  `id` bigint(20) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `percent` decimal(6,2) NOT NULL,
  `period_minutes` int(10) UNSIGNED NOT NULL CHECK (`period_minutes` >= 0),
  `run_minute` smallint(5) UNSIGNED NOT NULL CHECK (`run_minute` >= 0),
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `cashback_cashbacksettings`
--

INSERT INTO `cashback_cashbacksettings` (`id`, `enabled`, `percent`, `period_minutes`, `run_minute`, `updated_at`) VALUES
(1, 1, 10.00, 60, 0, '2025-09-13 16:18:40.303143');

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
(1, '2025-09-10 16:46:18.725280', '1', 'Обычный', 1, '[{\"added\": {}}]', 14, 1),
(2, '2025-09-10 16:48:09.842186', '1', 'Starter Box', 1, '[{\"added\": {}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"Small Reward ($1)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"Medium Reward ($3)\"}}, {\"added\": {\"name\": \"\\u041f\\u0440\\u0438\\u0437 \\u043a\\u0435\\u0439\\u0441\\u0430\", \"object\": \"Big Reward ($10)\"}}]', 12, 1),
(3, '2025-09-10 16:51:57.548099', '1', 'В ожидании (pending)', 1, '[{\"added\": {}}]', 7, 1),
(4, '2025-09-10 16:52:04.153717', '2', 'Подтверждено (approved)', 1, '[{\"added\": {}}]', 7, 1),
(5, '2025-09-10 16:52:10.905522', '3', 'Отклонено (rejected)', 1, '[{\"added\": {}}]', 7, 1),
(6, '2025-09-10 16:52:17.431750', '4', 'Отменено (cancelled)', 1, '[{\"added\": {}}]', 7, 1),
(7, '2025-09-10 16:52:36.962010', '1', 'В ожидании (pending)', 1, '[{\"added\": {}}]', 8, 1),
(8, '2025-09-10 16:52:43.454790', '2', 'Подтверждено (approved)', 1, '[{\"added\": {}}]', 8, 1),
(9, '2025-09-10 16:52:49.820798', '3', 'Отклонено (rejected)', 1, '[{\"added\": {}}]', 8, 1),
(10, '2025-09-10 16:52:56.542128', '4', 'Отменено (cancelled)', 1, '[{\"added\": {}}]', 8, 1),
(11, '2025-09-10 16:53:31.278028', '1', 'Deposit<1> anton.fa01@mail.ru $50 [В ожидании (pending)]', 1, '[{\"added\": {}}]', 11, 1),
(12, '2025-09-10 17:32:00.362116', '2', 'Deposit<2> anton.fa01@mail.ru $100 [В ожидании (pending)]', 1, '[{\"added\": {}}]', 11, 1),
(13, '2025-09-13 16:18:40.305142', '1', 'CashbackSettings object (1)', 1, '[{\"added\": {}}]', 20, 1);

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
(11, 'accounts', 'deposit'),
(7, 'accounts', 'depositstatus'),
(10, 'accounts', 'profile'),
(9, 'accounts', 'withdrawal'),
(8, 'accounts', 'withdrawalstatus'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(12, 'cases', 'case'),
(13, 'cases', 'caseprize'),
(14, 'cases', 'casetype'),
(15, 'cases', 'spin'),
(21, 'cashback', 'cashbackaccrual'),
(22, 'cashback', 'cashbackdebit'),
(20, 'cashback', 'cashbacksettings'),
(5, 'contenttypes', 'contenttype'),
(16, 'referrals', 'referrallevelconfig'),
(17, 'referrals', 'referralprofile'),
(6, 'sessions', 'session'),
(18, 'support', 'ticket'),
(19, 'support', 'ticketmessage');

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
(1, 'contenttypes', '0001_initial', '2025-09-08 11:20:07.888380'),
(2, 'auth', '0001_initial', '2025-09-08 11:20:08.347651'),
(3, 'accounts', '0001_initial', '2025-09-08 11:20:08.695904'),
(4, 'admin', '0001_initial', '2025-09-08 11:20:08.851980'),
(5, 'admin', '0002_logentry_remove_auto_add', '2025-09-08 11:20:08.859844'),
(6, 'admin', '0003_logentry_add_action_flag_choices', '2025-09-08 11:20:08.867842'),
(7, 'contenttypes', '0002_remove_content_type_name', '2025-09-08 11:20:08.915656'),
(8, 'auth', '0002_alter_permission_name_max_length', '2025-09-08 11:20:08.968843'),
(9, 'auth', '0003_alter_user_email_max_length', '2025-09-08 11:20:08.981600'),
(10, 'auth', '0004_alter_user_username_opts', '2025-09-08 11:20:08.988922'),
(11, 'auth', '0005_alter_user_last_login_null', '2025-09-08 11:20:09.025603'),
(12, 'auth', '0006_require_contenttypes_0002', '2025-09-08 11:20:09.029602'),
(13, 'auth', '0007_alter_validators_add_error_messages', '2025-09-08 11:20:09.036610'),
(14, 'auth', '0008_alter_user_username_max_length', '2025-09-08 11:20:09.049085'),
(15, 'auth', '0009_alter_user_last_name_max_length', '2025-09-08 11:20:09.060845'),
(16, 'auth', '0010_alter_group_name_max_length', '2025-09-08 11:20:09.073707'),
(17, 'auth', '0011_update_proxy_permissions', '2025-09-08 11:20:09.081707'),
(18, 'auth', '0012_alter_user_first_name_max_length', '2025-09-08 11:20:09.095273'),
(19, 'cases', '0001_initial', '2025-09-08 11:20:09.410020'),
(20, 'cashback', '0001_initial', '2025-09-08 11:20:09.526716'),
(21, 'referrals', '0001_initial', '2025-09-08 11:20:09.660794'),
(22, 'sessions', '0001_initial', '2025-09-08 11:20:09.719144'),
(23, 'support', '0001_initial', '2025-09-08 11:20:09.959379'),
(24, 'accounts', '0002_profile_client_seed_profile_pf_nonce', '2025-09-10 17:25:34.821574'),
(25, 'cases', '0002_spin_client_seed_spin_nonce_spin_rng_value_and_more', '2025-09-10 17:25:34.916380'),
(26, 'cashback', '0002_cashbackdebit', '2025-09-13 16:10:33.830892');

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
('6ajslq9dcxhoi981lswy2g4emku50gu3', '.eJxVjDsOwjAQBe_iGlle_0NJzxmstXeNAyiR4qRC3B0ipYD2zcx7iYTb2tLWeUkjibMAcfrdMpYHTzugO063WZZ5Wpcxy12RB-3yOhM_L4f7d9Cwt28dHDpNFhUWT4zWkIlWDxC1tzp7ztU45-pgBgAGAF-y8kyhRsRglBXvD9XJN2U:1uvZvv:nrXbNA3Sx9wbSqC5Mp7elJ-4Br-p9qQMT4KQZbI1L9o', '2025-09-22 11:21:15.131715');

-- --------------------------------------------------------

--
-- Структура таблицы `referrals_referrallevelconfig`
--

CREATE TABLE `referrals_referrallevelconfig` (
  `id` bigint(20) NOT NULL,
  `level` int(10) UNSIGNED NOT NULL CHECK (`level` >= 0),
  `percent` decimal(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(1, 'JE23ZSX5', NULL, NULL, 1),
(2, 'G52RNYZK', NULL, NULL, 2);

-- --------------------------------------------------------

--
-- Структура таблицы `support_ticket`
--

CREATE TABLE `support_ticket` (
  `id` bigint(20) NOT NULL,
  `subject` varchar(200) NOT NULL,
  `status` varchar(16) NOT NULL,
  `is_closed_by_user` tinyint(1) NOT NULL,
  `is_closed_by_staff` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `support_ticketmessage`
--

CREATE TABLE `support_ticketmessage` (
  `id` bigint(20) NOT NULL,
  `body` longtext NOT NULL,
  `attachment` varchar(100) DEFAULT NULL,
  `read_by_user_at` datetime(6) DEFAULT NULL,
  `read_by_staff_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `author_id` int(11) NOT NULL,
  `ticket_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `accounts_deposit`
--
ALTER TABLE `accounts_deposit`
  ADD PRIMARY KEY (`id`),
  ADD KEY `accounts_deposit_status_id_58f0575d_fk_accounts_depositstatus_id` (`status_id`),
  ADD KEY `accounts_deposit_user_id_7a9ea367_fk_auth_user_id` (`user_id`);

--
-- Индексы таблицы `accounts_depositstatus`
--
ALTER TABLE `accounts_depositstatus`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`);

--
-- Индексы таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `accounts_profile_client_seed_58bd5db3` (`client_seed`);

--
-- Индексы таблицы `accounts_withdrawal`
--
ALTER TABLE `accounts_withdrawal`
  ADD PRIMARY KEY (`id`),
  ADD KEY `accounts_withdrawal_status_id_db96bdf8_fk_accounts_` (`status_id`),
  ADD KEY `accounts_withdrawal_user_id_093546b4_fk_auth_user_id` (`user_id`);

--
-- Индексы таблицы `accounts_withdrawalstatus`
--
ALTER TABLE `accounts_withdrawalstatus`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`);

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
  ADD KEY `cases_spin_user_id_e33108d3_fk_auth_user_id` (`user_id`),
  ADD KEY `cases_spin_server_seed_hash_bf45ef8c` (`server_seed_hash`);

--
-- Индексы таблицы `cashback_cashbackaccrual`
--
ALTER TABLE `cashback_cashbackaccrual`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cashback_cashbackaccrual_user_id_slot_started_at_a9bdb960_uniq` (`user_id`,`slot_started_at`),
  ADD KEY `cashback_cashbackaccrual_slot_started_at_dfb79826` (`slot_started_at`),
  ADD KEY `cashback_cashbackaccrual_status_bbd1bbad` (`status`);

--
-- Индексы таблицы `cashback_cashbackdebit`
--
ALTER TABLE `cashback_cashbackdebit`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cashback_cashbackdebit_user_id_cf6a30c5_fk_auth_user_id` (`user_id`),
  ADD KEY `cashback_cashbackdebit_created_at_3ef57f84` (`created_at`),
  ADD KEY `cashback_cashbackdebit_status_1f5bb24f` (`status`);

--
-- Индексы таблицы `cashback_cashbacksettings`
--
ALTER TABLE `cashback_cashbacksettings`
  ADD PRIMARY KEY (`id`);

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
-- Индексы таблицы `referrals_referrallevelconfig`
--
ALTER TABLE `referrals_referrallevelconfig`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `level` (`level`);

--
-- Индексы таблицы `referrals_referralprofile`
--
ALTER TABLE `referrals_referralprofile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `referrals_referralpr_referred_by_id_d0360b18_fk_auth_user` (`referred_by_id`);

--
-- Индексы таблицы `support_ticket`
--
ALTER TABLE `support_ticket`
  ADD PRIMARY KEY (`id`),
  ADD KEY `support_ticket_user_id_d7c9336a_fk_auth_user_id` (`user_id`),
  ADD KEY `support_ticket_status_af97e066` (`status`);

--
-- Индексы таблицы `support_ticketmessage`
--
ALTER TABLE `support_ticketmessage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `support_ticketmessage_author_id_9766f73a_fk_auth_user_id` (`author_id`),
  ADD KEY `support_ticketmessage_ticket_id_70fe8f82_fk_support_ticket_id` (`ticket_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `accounts_deposit`
--
ALTER TABLE `accounts_deposit`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT для таблицы `accounts_depositstatus`
--
ALTER TABLE `accounts_depositstatus`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT для таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT для таблицы `accounts_withdrawal`
--
ALTER TABLE `accounts_withdrawal`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `accounts_withdrawalstatus`
--
ALTER TABLE `accounts_withdrawalstatus`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=89;

--
-- AUTO_INCREMENT для таблицы `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT для таблицы `cases_caseprize`
--
ALTER TABLE `cases_caseprize`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `cases_casetype`
--
ALTER TABLE `cases_casetype`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT для таблицы `cases_spin`
--
ALTER TABLE `cases_spin`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT для таблицы `cashback_cashbackaccrual`
--
ALTER TABLE `cashback_cashbackaccrual`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT для таблицы `cashback_cashbackdebit`
--
ALTER TABLE `cashback_cashbackdebit`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT для таблицы `cashback_cashbacksettings`
--
ALTER TABLE `cashback_cashbacksettings`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT для таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT для таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT для таблицы `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT для таблицы `referrals_referrallevelconfig`
--
ALTER TABLE `referrals_referrallevelconfig`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `referrals_referralprofile`
--
ALTER TABLE `referrals_referralprofile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT для таблицы `support_ticket`
--
ALTER TABLE `support_ticket`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `support_ticketmessage`
--
ALTER TABLE `support_ticketmessage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `accounts_deposit`
--
ALTER TABLE `accounts_deposit`
  ADD CONSTRAINT `accounts_deposit_status_id_58f0575d_fk_accounts_depositstatus_id` FOREIGN KEY (`status_id`) REFERENCES `accounts_depositstatus` (`id`),
  ADD CONSTRAINT `accounts_deposit_user_id_7a9ea367_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `accounts_profile`
--
ALTER TABLE `accounts_profile`
  ADD CONSTRAINT `accounts_profile_user_id_49a85d32_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `accounts_withdrawal`
--
ALTER TABLE `accounts_withdrawal`
  ADD CONSTRAINT `accounts_withdrawal_status_id_db96bdf8_fk_accounts_` FOREIGN KEY (`status_id`) REFERENCES `accounts_withdrawalstatus` (`id`),
  ADD CONSTRAINT `accounts_withdrawal_user_id_093546b4_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

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
-- Ограничения внешнего ключа таблицы `cashback_cashbackaccrual`
--
ALTER TABLE `cashback_cashbackaccrual`
  ADD CONSTRAINT `cashback_cashbackaccrual_user_id_ec82abb9_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `cashback_cashbackdebit`
--
ALTER TABLE `cashback_cashbackdebit`
  ADD CONSTRAINT `cashback_cashbackdebit_user_id_cf6a30c5_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

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

--
-- Ограничения внешнего ключа таблицы `support_ticket`
--
ALTER TABLE `support_ticket`
  ADD CONSTRAINT `support_ticket_user_id_d7c9336a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `support_ticketmessage`
--
ALTER TABLE `support_ticketmessage`
  ADD CONSTRAINT `support_ticketmessage_author_id_9766f73a_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `support_ticketmessage_ticket_id_70fe8f82_fk_support_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `support_ticket` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
