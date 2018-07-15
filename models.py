from abc import ABCMeta, abstractmethod


class InsertableModel():
    __metaclass__ = ABCMeta

    @staticmethod
    def to_sql_insert_template():
        raise NotImplementedError('subclasses must override to_sql_insert_template()!')

    @abstractmethod
    def to_sql_insert_params(self):
        raise NotImplementedError('subclasses must override to_sql_insert_params()!')


class Team:
    def __init__(self, id, name, handle):
        self.id = id
        self.name = name
        self.handle = handle


class Tweet(InsertableModel):
    def __init__(self, id, tweet_id, handle, epoch, body, likes, retweets):
        self.id = id
        self.tweet_id = tweet_id
        self.handle = handle
        self.epoch = epoch
        self.body = body
        self.likes = likes
        self.retweets = retweets

    @staticmethod
    def to_sql_insert_template():
        return '(%s,%s,%s,%s,%s,%s)'

    def to_sql_insert_params(self):
        return [self.tweet_id, self.handle, self.epoch, self.body, self.likes, self.retweets]


class TweetBucket(InsertableModel):
    def __init__(self, id, handle, bucket_start, count, likes, retweets):
        self.id = id
        self.handle = handle
        self.bucket_start = bucket_start
        self.count = count
        self.likes = likes
        self.retweets = retweets

    @staticmethod
    def to_sql_insert_template():
        return '(%s,%s,%s,%s,%s)'

    def to_sql_insert_params(self):
        return [self.handle, self.bucket_start, self.count, self.likes, self.retweets]

    def increment_stats(self, tweet):
        self.count += 1
        self.likes += tweet.likes
        self.retweets += tweet.retweets
