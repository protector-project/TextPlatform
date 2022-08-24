import pandas as pd
from dagster import get_dagster_logger, job, op
from minio import Minio

from components.protector_emotions.src.predict_emotions import predict_emotions
from components.twitter_api_converter.src.converter import convert_tweets
from components.twitter_tsv_converters.src.converters import (
    convert_to_tsv,
    convert_tsv_to_influx,
)


@op(
    config_schema={
        "MINIO_ADDRESS": str,
        "MINIO_ACCESS_KEY": str,
        "MINIO_SECRET_KEY": str,
    }
)
def load_envs(context) -> dict:
    config = {
        "MINIO_ADDRESS": context.op_config["MINIO_ADDRESS"],
        "MINIO_ACCESS_KEY": context.op_config["MINIO_ACCESS_KEY"],
        "MINIO_SECRET_KEY": context.op_config["MINIO_SECRET_KEY"],
    }
    return config


@op(config_schema={"bucket_name": str, "file_name": str})
def download_raw_data(context, env_values: dict) -> list:
    client = Minio(
        env_values["MINIO_ADDRESS"],
        access_key=env_values["MINIO_ACCESS_KEY"],
        secret_key=env_values["MINIO_SECRET_KEY"],
        secure=False,
    )
    bucket_name = context.op_config["bucket_name"]
    input_name = context.op_config["file_name"]
    output_name = "local_test.json"
    obj = client.get_object(
        bucket_name,
        input_name,
        output_name,
    )
    encoding = "utf-8"
    return [str(line, encoding) for line in obj]


@op(config_schema={"bucket_name": str, "file_name": str})
def upload_influx(context, env_values: dict, input_file: list):
    from io import BytesIO

    client = Minio(
        env_values["MINIO_ADDRESS"],
        access_key=env_values["MINIO_ACCESS_KEY"],
        secret_key=env_values["MINIO_SECRET_KEY"],
        secure=False,
    )
    bucket_name = context.op_config["bucket_name"]
    input_name = context.op_config["file_name"]

    b_input_file = "\n".join(input_file).encode("utf-8")
    stream_input_file = BytesIO(b_input_file)

    client.put_object(
        bucket_name,
        input_name,
        data=stream_input_file,
        length=len(b_input_file),
        content_type="application/json",
    )


@op
def merge_data(emotions: list, h_speech: list) -> list:
    return emotions + h_speech


@op
def display_results(obj: list):
    logger = get_dagster_logger()
    for line in obj:
        logger.info(f"RAW DATA: {line}")


@op
def convert_twitter_data(raw_data: list) -> list:
    converted_json = convert_tweets(raw_data)
    return converted_json


@op(config_schema={"lang_code": str, "local": str})
def detect_emotions(context, input_file: list) -> list:
    return predict_emotions(
        input_file, context.op_config["lang_code"], "tw", context.op_config["local"]
    )


@op
def convert_json_to_tsv(input_file: list) -> pd.DataFrame:
    return convert_to_tsv(input_file)


@op(config_schema={"tmp_folder": str, "model_folder": str, "model_name": str})
def run_h_speech(context, input_text: pd.DataFrame) -> pd.DataFrame:
    input_text.to_csv(
        "{}/input.tsv".format(context.op_config["tmp_folder"]),
        index=False,
        header=False,
        sep="\t",
    )
    from subprocess import PIPE, Popen

    c = (
        "docker run -it -v {}:/app/model"
        " -v {}:/app/tmp hate-speech-detector:devel"
        " python machamp/predict.py /app/model/{} /app/tmp/input.tsv /app/tmp/out.tsv --device -1".format(
            context.op_config["model_folder"],
            context.op_config["tmp_folder"],
            context.op_config["model_name"],
        )
    )
    c_ = c.split(" ")
    process = Popen(c_, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    df = pd.read_csv(
        "{}/out.tsv".format(context.op_config["tmp_folder"]), sep="\t", header=None
    )
    return df


@op(config_schema={"language": str, "local": str})
def tsv_to_json(context, results: pd.DataFrame) -> list:
    return convert_tsv_to_influx(
        results, context.op_config["local"], context.op_config["language"]
    )


@job
def run_twitter_pipeline():
    env_values = load_envs()
    raw_data = download_raw_data(env_values)
    converted_tweets = convert_twitter_data(raw_data)
    influx_emotions = detect_emotions(converted_tweets)
    tsv_tweets = convert_json_to_tsv(converted_tweets)
    output_h = run_h_speech(tsv_tweets)
    influx_h = tsv_to_json(output_h)
    display_results(influx_emotions)
    display_results(influx_h)
    all_data = merge_data(influx_emotions, influx_h)
    upload_influx(env_values, all_data)
