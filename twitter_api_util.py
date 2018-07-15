import requests

from dateutil import parser

from models import Tweet


class TwitterApiUtil:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def fetch_tweets(self, handle, max_id = None):
        """
        :param token: bearer token for twitter auth
        :param handle: twitter handle
        :param max_id: max id of messages to receive (used for paging)
        :return: list of tweets from the handle's timeline in descending chronological order
        """
        headers = {
            'Authorization': 'Bearer %s' % self.bearer_token
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
        for status in response_json:
            date = parser.parse(status['created_at'])
            epoch = date.strftime("%s")

            tweet = Tweet(None, status['id'], status['user']['screen_name'], epoch, status['text'], status['favorite_count'], status['retweet_count'])
            tweets.append(tweet)

        return tweets
