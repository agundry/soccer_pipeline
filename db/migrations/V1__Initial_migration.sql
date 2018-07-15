CREATE TABLE `teams` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `twitter_handle` varchar(30) UNIQUE NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED;

CREATE TABLE `tweets` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `tweet_id` bigint UNIQUE NOT NULL,
  `handle` varchar(30) NOT NULL,
  `epoch` varchar(30) NOT NULL,
  `body` text NOT NULL,
  `likes` int(11) NOT NULL,
  `retweets` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED;

CREATE TABLE `tweet_buckets` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `handle` varchar(30) NOT NULL,
  `bucket_start` datetime(3) NOT NULL,
  `count` int(11) NOT NULL,
  `likes` int(11) NOT NULL,
  `retweets` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `handle_bucket` (`handle`, `bucket_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED;
