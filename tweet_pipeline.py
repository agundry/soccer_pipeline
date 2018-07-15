import yaml

from models import TweetBucket
from db_util import SoccerDbConnectionFactory
from db_util import SoccerDbi
from helpers import get_bucket_start_from_epoch
from config import PipelineConfig
from twitter_api_util import TwitterApiUtil


def roll_up_tweets(bucket_store, tweets):
    """
    Aggregates tweets into existing bucket store to roll up engagement metrics

    :param bucket_store: existing bucket store of engagement data
    :param tweets: tweets to be aggregated
    """
    for tweet in tweets:
        bucket_start = get_bucket_start_from_epoch(int(tweet.epoch))
        bucket_tuple = (tweet.handle, bucket_start)

        if bucket_store.get(bucket_tuple, None):
            bucket_store.get(bucket_tuple).increment_stats(tweet)
        else:
            new_bucket = TweetBucket(None, tweet.handle, bucket_start, 1, tweet.likes, tweet.retweets)
            bucket_store[bucket_tuple] = new_bucket


def run_pipeline(soccer_dbi, twitter_client):
    """
    Queries teams from the database and fetches timelines for each team's handle
    Tweets are stored both individually in the database as well as rolled up into monthly buckets for engagement totals

    :param soccer_dbi: dbi for soccer database
    :param twitter_client: client for twitter api
    """
    bucket_store = {}
    teams = soccer_dbi.fetch_teams()
    for team in teams:
        print 'Backfilling team %s' % team.name
        last_id = None
        for index in xrange(1,101):
            print '\tRequest %s' % index
            # time.sleep(1)  # self-induced rate limiting optional
            tweets = twitter_client.fetch_tweets(team.handle, max_id=last_id)

            # Continue requesting until we no longer receive tweets (public api gives us 3200 per timeline)
            if tweets:
                soccer_dbi.insert_tweets(tweets)
                roll_up_tweets(bucket_store, tweets)
                last_id = tweets[len(tweets) - 1].tweet_id - 1
            else:
                print '\tEmpty tweet response, skipping'
                break

        # Persist and clear aggregated buckets from bucket_store
        soccer_dbi.insert_buckets(bucket_store.values())
        bucket_store.clear()


if __name__ == '__main__':
    # Load config
    config = None
    with open("config.yaml", 'r') as config_file:
        data_loaded = yaml.load(config_file)
        config = PipelineConfig(**data_loaded)

    # Initialize db stuff
    connection_factory = SoccerDbConnectionFactory(config.db.host,
                                                   config.db.port,
                                                   config.db.name,
                                                   config.db.user,
                                                   config.db.password)
    db_connection = connection_factory.fetch_connection()
    soccer_dbi = SoccerDbi(db_connection)

    # Initialize twitter api helper
    twitter_client = TwitterApiUtil(config.bearer_token)

    run_pipeline(soccer_dbi, twitter_client)
