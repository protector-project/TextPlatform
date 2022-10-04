from dagster import sensor, RunRequest, DefaultSensorStatus, repository
from minio import Minio
from minio.commonconfig import Tags

from y_sensor import my_bucket_sensor_youtube
from t_sensor import my_bucket_sensor_twitter

@repository
def my_repository():
    return [my_bucket_sensor_twitter, my_bucket_sensor_youtube]