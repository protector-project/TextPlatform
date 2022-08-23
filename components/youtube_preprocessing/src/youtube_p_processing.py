import pandas as pd
import re


def convert_yt_tsv_json(df):
    df.columns = ["label", "text", "created_at", "id"]

    df["created_at"] = pd.to_datetime(df.created_at)
    df["created_at"] = df["created_at"].dt.strftime("%a %b %d %H:%M:%S +0000 %Y")

    data = []
    for i in range(len(df)):
        data.append(str(df.loc[i].to_json()))

    return data


def preprocess_yt_tsv(df):
    data = []
    for index in range(len(df)):

        # anonymize
        text = df["text"].loc[index].lower()
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")

        # 3) Anonymization: replace email addresses, usernames, and URLS
        text = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text)
        text = re.sub(r"@[A-Za-z0-9_-]+", "[USER]", text)
        text = re.sub(r"http[^\r\n\t\f\v )\]\}]+", "[URL]", text)

        csv_row = {
            "label": "NOT RELIGIOUS HATE",
            "text": text,
            "create_at": str(df["date"].loc[index]),
            "video_id": str(df["video_id"].loc[index]),
        }

        data.append(csv_row)

    df2 = pd.DataFrame(data)
    return df2


def tsv_to_influx(df, local, language):
    df.columns = ["label", "text", "create_at", "video_id"]
    data = []
    for i in range(len(df)):
        if df["label"].loc[i] == "RELIGIOUS HATE":
            json_body = [
                {
                    "time": df["create_at"].loc[i],
                    "measurement": "youtube_hate",
                    "tags": {
                        "video_id": df["video_id"].loc[i],
                        "country": local,
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
