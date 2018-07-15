from helpers import dotdict


class PipelineConfig:
    def __init__(self, bearer_token, db):
        self.bearer_token = bearer_token
        self.db = dotdict()
        self.db['host'] = db['host']
        self.db['user'] = db['user']
        self.db['port'] = db['port']
        self.db['name'] = db['name']
        self.db['password'] = db['password']
