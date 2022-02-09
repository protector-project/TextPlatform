from influxdb import InfluxDBClient
import json

class InfluxClient:
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.client = None

    def ping(self):
        return self.client.ping()

    def createConnection(self):
        try:
            self.client = InfluxDBClient(
                host=self.host, port=self.port, database=self.database
            )
        except Exception as e:
            print(e)

    def insert_tweet(self, tweet, classification):
        t = json.loads(tweet)
        if classification == 1:
            self.insert_geo(tweet)
        json_body = [
            {
                "time": t["created_at"],
                "measurement": "hate",
                "tags": {"tweet_id": t["id"]},
                "fields": {"classification": classification},
            }
        ]
        self.client.write_points(json_body)

    def insert_emotions(self, tweet, data):
        t = json.loads(tweet)
        for k, v in data.items():
            if v == 0 or v == 1:
                data[k] = float(v)
            else:
                data[k] = float(2)
        json_body = [
            {
                "time": t["created_at"],
                "measurement": "emotions",
                "tags": {"tweet_id": t["id"]},
                "fields": data,
            }
        ]
        self.client.write_points(json_body)

    def insert_geo(self, tweet):
        t = json.loads(tweet)
        json_body = [
            {
                "time": t["created_at"],
                "measurement": "locations",
                "tags": {"tweet_id": t["id"]},
                "fields": {"geohash": 'sr2ykk5t6kvug'},
            }
        ]
        self.client.write_points(json_body)