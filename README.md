# PROTECTOR Text Pipeline

## Installation

We recomend to create a conda enviroment:

``conda create -n text_pipeline python==3.9``

Next, install the requirements

``pip install -r requirements.txt``

Install language packs:

English: ``python -m spacy download en_core_web_lg``

Italian: ``python -m spacy download it_core_news_lg``

Create folders for the model and temporary files:

``mkdir ml_models && mkdir tmp``

Create Hate Speech Container:

`cd components/protector_hate_speech/`

`bash build.sh`



## How to Run

### Single File

``conda activate text_pipeline``

``dagit -f twitter_pipeline.py``

In the launchpad add the configuration of the file `config_files/t_config.yaml`

### Using Sensor

Watch a MinIO bucket and create new runs for files being uploaded

Change the workspace.yaml file for the ``y_sensor.py`` for YouTube or ``t_sensor.py`` for Twitter.

Create a folder to store Dagster information:

``mkdir -p /home/vbezerra/dagster``

Run the daemon in background:

``DAGSTER_HOME=/home/vbezerra/dagster dagster-daemon run``

Run Dagit in a new window:

``DAGSTER_HOME=/home/vbezerra/dagster dagit``
