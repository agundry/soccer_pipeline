import requests
import urllib
import base64

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

"""
    This script can be used to fetch an application-only bearer token for use with the twitter public api
"""
if __name__ == '__main__':
    consumer_key = urllib.quote(CONSUMER_KEY)
    consumer_secret = urllib.quote(CONSUMER_SECRET)
    bearer_token = consumer_key + ':' + consumer_secret
    base64_encoded_bearer_token = base64.b64encode(bearer_token)
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': 'Basic %s' % base64_encoded_bearer_token
    }

    data = {
            'grant_type': 'client_credentials'
    }

    url = 'https://api.twitter.com/oauth2/token'
    response = requests.post(url, headers=headers, data=data)

    print 'Bearer %s' % response.content
