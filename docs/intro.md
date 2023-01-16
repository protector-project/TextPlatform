# Introduction

The Text Platform repository is reponsable for processing Twitter and Youtube data and creating json files with metrics about the emotions, hate speech tweets and more.

## Folder Structure

This repository is organised in the folowing structure:

### Components

In this folder are stored the source code files responsable for processing the data

``protector_emotions``: Emotion predictor

``protector_hate_speech``: Hate speech detector

``twitter_api_converter``: Functions responsable for converting Twitter files from the old API to the new

``twitter_tsv_converters``: Series of functions reponsable for converting json and tsv files 

``youtube_p_processing``: Functions for the pre processing of raw data from YouTube

### Configuration Files (config_files)

This folder contains configuration files for Dagster for Twitter processing (``t_config.yaml``) and Youtube (``yt_config.yaml``)

### Root Files

``Dockerfile``: Docker File 

``build.sh``: script to build the Docker Image

``main.py``: agregator of the Dagster sensors

``requirements.txt``: list of Python libraries required to run the project

``run.sh``: script responsable for running the Docker image

``t_sensor.py``: Dagster sensor for running the Twitter pipeline

``twitter_pipeline.py``: Dagster pipeline for Twitter data

``workspace.yaml``: Dagster configuration file

``y_sensor.py``: Dagster sensor for running the Youtube pipeline

``youtube_pipeline.py``: Dagster pipeline for Youtube data

