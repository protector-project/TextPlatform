import json

DOWNLOADER_WITH_CONFIG = ['s3', 'aws', 'minio']
SUPPORTED_DOWNLOADER = ['http', 'https','s3', 'aws', 'minio']
MODEL_CONFIG = "MODEL_CONFIG"

def download_from_config(config):
    print_obj_from_json(config)
    check_config_json(config)
    if config["type"] == 'http' or config["type"] == 'https':
        download_file_http(config["uri"], config["path"])
    elif config["type"] == 's3' or config["type"] == 'aws':
        download_file_s3(config["uri"],config["path"], config["config"])
    # elif config["type"] == 'google' or config["type"] == 'gs':
    #     download_file_google_storage(config["uri"], config["path"], config["config"])
    elif config["type"] == 'minio':
        download_file_minio(config["uri"],config["path"], config["config"])
    else:
        type_not_implemented = config["type"]
        raise Exception(
            f"Type parameters not yet implemented or does not exist: {type_not_implemented}, the one supported are: {SUPPORTED_DOWNLOADER}")


def download_file_http(url, path: str = None):
    import requests
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    if path != None:
        local_filename = path
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
            print(f"File downloaded in : {local_filename}")
    return local_filename


def download_file_s3(endpoint: str,path: str = None, config: object = None):
    import boto3
    s3 = boto3.client(endpoint,aws_access_key_id=config["access_key"] , aws_secret_access_key= config["secret_key"])
    check_config_for_s3_minio(config)
    s3.download_file(config['BUCKET_NAME'],
                     config['OBJECT_NAME'], path)
    print(f"File downloaded in : {path}")


def check_config_for_s3_minio(config: object = None):
    try:
        if config['access_key'] == None or config['access_key'] == "":
            value = config['access_key']
            raise Exception("Value for config access_key must be provided, value given: {value}")
        if config['secret_key'] == None or config['secret_key'] == "":
            value = config['secret_key']
            raise Exception("Value for config secret_key must be provided, value given: {value}")
        if config['BUCKET_NAME'] == None or config['BUCKET_NAME'] == "":
            BUCKET_NAME = config['BUCKET_NAME']
            raise Exception(
                f"Config value in the {MODEL_CONFIG}, BUCKET_NAME: value provided: {BUCKET_NAME}, not valid.")
        if config['OBJECT_NAME'] == None or config['OBJECT_NAME'] == "":
            OBJECT_NAME = config['OBJECT_NAME']
            raise Exception(
                f"Config value in the {MODEL_CONFIG}, OBJECT_NAME: value provided: {OBJECT_NAME}, not valid.")
    except:
        raise Exception(
            f"Config value in the {MODEL_CONFIG} env not valid for s3.")


# def download_file_google_storage(url, path: str = None, config: object = None):
#     #https://stackoverflow.com/questions/42555142/downloading-a-file-from-google-cloud-storage-inside-a-folder
#     from google.cloud import storage
#     # Initialise a client
#     storage_client = storage.Client(config['OBJECT_NAME'])
#     # Create a bucket object for our bucket
#     bucket = storage_client.get_bucket(config['OBJECT_NAME'])
#     # Create a blob object from the filepath
#     blob = bucket.blob("folder_one/foldertwo/filename.extension")
#     # Download the file to a destination
#     blob.download_to_filename(path)


def download_file_minio(endpoint: str,path: str = None, config: object = None):
    from minio import Minio
    check_config_for_s3_minio(config)
    client = Minio(endpoint,access_key=config["access_key"],secret_key= config["secret_key"],secure=False)
    client.fget_object(config["BUCKET_NAME"],config["OBJECT_NAME"],path)
    print(f"File downloaded in : {path}")

def check_config_json(json_obj: object):
    try:
        type_ = json_obj["type"]
        if type_ == None or type_ == "":
            raise Exception(f"Type value in the {MODEL_CONFIG} env is None.")
        if not type_ in SUPPORTED_DOWNLOADER:
            raise Exception(f"Type value in the {MODEL_CONFIG} env is not supported: {type_} , the one supported are: {SUPPORTED_DOWNLOADER}.")
    except:
        raise Exception(f"Type value in the {MODEL_CONFIG} env not provided.")
    try:
        uri = json_obj["uri"]
        if uri == None or uri == "":
            raise Exception(f"Uri value in the {MODEL_CONFIG} env is None.")
    except:
        raise Exception(f"Uri value in the {MODEL_CONFIG} env not provided.")
    try:
        path = json_obj["path"]
        if path == None or path == "":
            raise Exception(f"Path value in the {MODEL_CONFIG} env is None.")
    except:
        raise Exception(f"Path value in the {MODEL_CONFIG} env not provided.")
    try:
        if (json_obj["type"] in DOWNLOADER_WITH_CONFIG):
            config = json_obj["config"]
            if config == None or config == "" or config == {}:
                raise Exception(
                    f"Config value in the {MODEL_CONFIG} env is None.")
    except:
        raise Exception(f"Config value in the {MODEL_CONFIG} env not valid.")


def config_s3_str_example():
    return '{"access_key": "access_key" , "secret_key": "secret_key", "BUCKET_NAME":"BUCKET_NAME","OBJECT_NAME": "OBJECT_NAME", "references_not_to_provide": ["when creating the config json this field must not be passed","https://stackoverflow.com/questions/50100221/download-file-from-aws-s3-using-python","https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.download_file"]}'

def json_config_s3_example():
    json_data = config_s3_str_example()
    return json.loads(json_data)

def json_s3_example():
    config = config_s3_str_example()
    json_str = '{"type": "s3","uri": "s3_endpoint", "path": "path_where_to_save_model", "config": '+config+'}'
    return json.loads(json_str)

def config_minio_str_example():
    return '{"access_key": "access_key" , "secret_key": "secret_key", "BUCKET_NAME":"BUCKET_NAME","OBJECT_NAME": "OBJECT_NAME", "references_not_to_provide": ["when creating the config json this field must not be passed","https://min.io/docs/minio/linux/developers/python/minio-py.html"]}'

def json_config_minio_example():
    json_data = config_minio_str_example()
    return json.loads(json_data)

def json_minio_example():
    config = config_minio_str_example()
    json_str = '{"type": "minio", "uri": "minio_endpoint", "path": "path_where_to_save_model", "config": '+config+'}'
    return json.loads(json_str)

def json_http_example():
    json_str = '{"type": "http", "uri": "http_endpoint","path": "path_where_to_save_model"}'
    return json.loads(json_str)


def print_obj_from_json(obj):
    json_formatted_str = json.dumps(obj, indent=2)
    print(json_formatted_str)

def json_config_gs_example():
    print()


def get_services():
    print(SUPPORTED_DOWNLOADER)

def get_services_with_config():
    print(DOWNLOADER_WITH_CONFIG)

def print_config_s3():
    print_obj_from_json(json_s3_example())

def print_config_minio():
    print_obj_from_json(json_minio_example())

def print_config_http():
    print_obj_from_json(json_http_example())
