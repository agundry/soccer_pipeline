import requests
import pymysql.cursors
from dateutil import parser
import datetime

BEARER_TOKEN = ''


class SoccerDbConnectionFactory:
    def __init__(self, host, port, db, user, password):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

    def fetch_connection(self):
        return pymysql.connect(host=self.host,
                               user=self.user,
                               password=self.password,
                               db=self.db,
                               charset='utf8mb4',
                               port=self.port,
                               cursorclass=pymysql.cursors.DictCursor)


class SoccerDbi():
    def __init__(self, connection):
        self.connection = connection

    def fetch_teams(self):
        with self.connection.cursor() as cursor:
            query = ("SELECT id, name, twitter_handle FROM teams;")
            cursor.execute(query)

            teams = []
            rows = cursor.fetchall()
            for row in rows:
                teams.append(Team(row['id'], row['name'], row['twitter_handle']))
            return teams

    def insert_tweets(self, tweets):
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO tweets (tweet_id, handle, epoch, body, likes, retweets) " + \
                        "VALUES "
                inserts = [Tweet.to_sql_insert_template() for _ in tweets]
                query += ','.join(inserts)

                params_list = [tweet.to_sql_insert_params() for tweet in tweets]
                params = [item for sublist in params_list for item in sublist]

                cursor.execute(query, params)
        except Exception as e:
            print e
        finally:
            self.connection.commit()

    def insert_buckets(self, buckets):
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO tweet_buckets (handle, bucket_start, `count`, likes, retweets) " + \
                        "VALUES "
                inserts = [TweetBucket.to_sql_insert_template() for _ in buckets]
                query += ','.join(inserts)

                params_list = [bucket.to_sql_insert_params() for bucket in buckets]
                params = [item for sublist in params_list for item in sublist]

                cursor.execute(query, params)
        except Exception as e:
            print e
        finally:
            self.connection.commit()


class Team:
    def __init__(self, id, name, handle):
        self.id = id
        self.name = name
        self.handle = handle


class Tweet:
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

class TweetBucket:
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


def fetch_tweets(handle, max_id = None):
    headers = {
        'Authorization': 'Bearer %s' % BEARER_TOKEN
    }

    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=200' % handle
    if max_id:
        url += '&max_id=%s' % max_id

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print response.content
        print response.status_code
        raise Exception("Error fetching tweets")

    response_json = response.json()

    tweets = []
    if not response_json:
        return tweets

    for status in response_json:
        date = parser.parse(status['created_at'])
        epoch = date.strftime("%s")

        tweet = Tweet(None, status['id'], status['user']['screen_name'], epoch, status['text'], status['favorite_count'], status['retweet_count'])
        tweets.append(tweet)

    return tweets


def get_bucket_start_from_epoch(epoch):
    epoch_dt = datetime.datetime.utcfromtimestamp(epoch)
    epoch_dt_rounded = epoch_dt.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    return epoch_dt_rounded


def roll_up_tweets(bucket_store, tweets):
    for tweet in tweets:
        bucket_start = get_bucket_start_from_epoch(int(tweet.epoch))
        bucket_tuple = (tweet.handle, bucket_start)

        if bucket_store.get(bucket_tuple, None):
            bucket_store.get(bucket_tuple).increment_stats(tweet)
        else:
            new_bucket = TweetBucket(None, tweet.handle, bucket_start, 1, tweet.likes, tweet.retweets)
            bucket_store[bucket_tuple] = new_bucket


if __name__ == '__main__':
    connection_factory = SoccerDbConnectionFactory('localhost',13306,'soccer','root','my-secret-pw')
    db_connection = connection_factory.fetch_connection()
    soccer_dbi = SoccerDbi(db_connection)

    bucket_store = {}

    teams = soccer_dbi.fetch_teams()
    for team in teams:
        print 'Backfilling team %s' % team.name
        last_id = None
        for index in xrange(1,101):
            print '\tRequest %s of 100' % index
            # time.sleep(1)  # self-induced rate limiting
            tweets = fetch_tweets(team.handle, max_id=last_id)
            if tweets:
                soccer_dbi.insert_tweets(tweets)
                roll_up_tweets(bucket_store, tweets)
                last_id = tweets[len(tweets) - 1].tweet_id - 1
            else:
                print '\tEmpty tweet response, skipping'
                break

        soccer_dbi.insert_buckets(bucket_store.values())
        bucket_store.clear()
