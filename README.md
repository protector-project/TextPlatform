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

``conda activate text_pipeline``

``dagit -f twitter_pipeline.py``

In the launchpad add the configuration of the file `config_files/t_config.yaml`
