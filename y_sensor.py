from dagster import sensor, RunRequest, DefaultSensorStatus, repository
from minio import Minio
from minio.commonconfig import Tags
from youtube_pipeline import load_envs, run_youtube_pipeline
import os

@sensor(job=run_youtube_pipeline)
def my_bucket_sensor_youtube():
    envs = {
        "MINIO_ADDRESS": os.environ.get("MINIO_ADDRESS"),
        "MINIO_ACCESS_KEY": os.environ.get("MINIO_ACCESS_KEY"),
        "MINIO_SECRET_KEY": os.environ.get("MINIO_SECRET_KEY"),
        "RAW_BUCKET": os.environ.get("RAW_BUCKET_YOUTUBE"),
        "AN_BUCKET": os.environ.get("AN_BUCKET_TWITTER"),
    }

    model_names = {
        "it": "it/model_it.tar.gz",
        "bg": "bg/model_bg.tar.gz",
        "en": "en/model_en.tar.gz",
    }

    client = Minio(
        envs["MINIO_ADDRESS"],
        access_key=envs["MINIO_ACCESS_KEY"],
        secret_key=envs["MINIO_SECRET_KEY"],
        secure=False,
    )
    bucket_name = envs["RAW_BUCKET"]
    response = client.list_objects(bucket_name, recursive=True)
    for resp in response:
        tags = client.get_object_tags("protector", resp.object_name)

        # get file language
        # the file must follow the name scheme date_local_language.json
        info = resp.object_name.split(".")[0].split("_")
        lang = info[-1]
        local = info[-2]
        model_to_be_used = model_names[lang]

        if tags == None or tags["status"] != "processed":
            # create run
            yield RunRequest(
                run_key=resp.object_name,
                run_config={
                    "ops": {
                        "load_envs": {
                            "config": {
                                "MINIO_ADDRESS": envs["MINIO_ADDRESS"],
                                "MINIO_ACCESS_KEY": envs["MINIO_ACCESS_KEY"],
                                "MINIO_SECRET_KEY": envs["MINIO_SECRET_KEY"],
                            }
                        },
                        "download_raw_data": {
                            "config": {
                                "bucket_name": envs["RAW_BUCKET"],
                                "file_name": resp.object_name,
                            }
                        },
                        "detect_emotions": {
                            "config": {"lang_code": lang, "local": local}
                        },
                        "run_h_speech": {
                            "config": {
                                "model_name": model_to_be_used,
                            }
                        },
                        "create_influx": {"config": {"language": lang, "local": local}},
                        "upload_influx": {
                            "config": {
                                "bucket_name": envs["AN_BUCKET"],
                                "file_name": resp.object_name + "_influx.json",
                            }
                        },
                    }
                },
            )

            if tags == None:
                tags = Tags.new_object_tags()
            tags["status"] = "processed"
            client.set_object_tags(bucket_name, resp.object_name, tags)


@repository
def my_repository():
    return [run_youtube_pipeline, my_bucket_sensor_youtube]
