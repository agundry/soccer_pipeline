import pymysql.cursors
from models import Team
from models import Tweet
from models import TweetBucket


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
                query = "INSERT INTO tweets (tweet_id, handle, epoch, body, likes, retweets) VALUES "
                inserts = [Tweet.to_sql_insert_template() for _ in tweets]
                query += ','.join(inserts)

                params_list = [tweet.to_sql_insert_params() for tweet in tweets]
                params = [item for sublist in params_list for item in sublist]

                cursor.execute(query, params)
        except Exception as e:
            raise Exception("Could not insert tweets")
        finally:
            self.connection.commit()

    def insert_buckets(self, buckets):
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO tweet_buckets (handle, bucket_start, `count`, likes, retweets) VALUES "
                inserts = [TweetBucket.to_sql_insert_template() for _ in buckets]
                query += ','.join(inserts)

                params_list = [bucket.to_sql_insert_params() for bucket in buckets]
                params = [item for sublist in params_list for item in sublist]

                cursor.execute(query, params)
        except Exception as e:
            raise Exception("Could not insert buckets")
        finally:
            self.connection.commit()
