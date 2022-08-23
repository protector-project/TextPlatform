import json
import re

import pandas as pd


def convert_to_tsv(json_file):
    data = []
    for j_object in json_file:
        json_dict = json.loads(j_object)
        post = json_dict["text"]

        # remove formating text
        text = post.lower()
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")

        # 3) Anonymization: replace email addresses, usernames, and URLS
        text = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text)
        text = re.sub(r"@[A-Za-z0-9_-]+", "[USER]", text)
        text = re.sub(r"http[^\r\n\t\f\v )\]\}]+", "[URL]", text)

        # create row and random label
        csv_row = {
            "label": "NOT RELIGIOUS HATE",
            "text": text,
            "create_at": str(json_dict["created_at"]),
            "twitter_id": str(json_dict["id"]),
        }

        data.append(csv_row)

    df = pd.DataFrame(data)
    return df


def convert_tsv_to_influx(df: pd.DataFrame, country: str, language: str) -> list:
    data = []
    df.columns = ["label", "text", "time", "id"]
    for i in range(len(df)):
        if df["label"].loc[i] == "RELIGIOUS HATE":
            json_body = [
                {
                    "time": df["time"].loc[i],
                    "measurement": "hate",
                    "tags": {
                        "tweet_id": df["id"].loc[i],
                        "country": country,
                        "language": language,
                    },
                    "fields": {
                        "classification": df["label"].loc[i],
                        "text": df["text"].loc[i],
                    },
                }
            ]
            data.append(json_body)

    return data
