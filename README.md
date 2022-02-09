# PROTECTOR TWITTER

### Requirements

It is recommended to install an environment management system (e.g., miniconda3) to avoid conflicts with other programs. After installing miniconda3, create the environment `$ENV_NAME` and install the packages from `requirements.txt`:

```
cd $PROJECT_DIR                           # access the folder relative to this project
conda create --name $ENV_NAME python=3.8  # create a python 3.8 environment $ENV_NAME
conda activate $ENV_NAME                  # activate the environment $ENV_NAME
python -m pip install -r requirements.txt # install packages from requirements.txt
python -m spacy download en_core_web_sm   # install spacy en language model
```

Alternatively, you can also install python 3.8 and packages from `requirements.txt` manually. However, there is no guarantee that the package versions will match those from the requirements.

### Usage

In the following we outline (1) how to run the hate speech detection model on tweets and (2) how to run the emotion detection algorithm on tweets.

##### Run the hate speech detection model on tweets

In order to classify tweets (and store the results to an output file `$OUTPUT_FILEPATH`), create a json line input file `$INPUT_FILEPATH` containing a tweet per line, with at least two keys: `id` and `text`. An example follows, while a sample file is `data/example.jsonl`.

```
{"id": 001, "text": "Text of tweet 001", "optional_key": "content of optional additional key"}
{"id": 002, "text": "Text of tweet 002", "optional_key": "content of optional additional key"}
...
{"id": 100, "text": "Text of tweet 100", "optional_key": "content of optional additional key"}
```

Then, just run the following command to predict the hate/not-hate content of each tweet:

`python predict_hate.py -I $INPUT_FILEPATH > $OUTPUT_FILEPATH`

where:
- `$INPUT_FILEPATH` (**required**): the path to the json line file with tweets to classify (with at least two keys: "id" and "text").

The output file will contain an additional column indicating if the tweet has been classified as hateful or not hateful (`hate` if hate speech, `not-hate` otherwise). An example follows.

```
{"id": 001, "text": "Text of tweet 001", "optional_key": "content of optional additional key"}	not-hate
{"id": 002, "text": "Text of tweet 002", "optional_key": "content of optional additional key"}	hate
...
{"id": 100, "text": "Text of tweet 100", "optional_key": "content of optional additional key"}	not-hate
```


##### Run the emotion detection algorithm on tweets

In order to detect NRC emotions on tweets (and store the results to output files starting with `$OUTPUT_BASE_FILEPATH`), create a json line input file `$INPUT_FILEPATH` containing a tweet per line, with at least three keys: `id`, `text`, and `created_at`. An example follows, while a sample file is `data/example.jsonl`.

```
{"id": 001, "text": "Text of tweet 001", "created_at": "2021-02-08T02:06:18.000Z", "optional_key": "content of optional additional key"}
{"id": 002, "text": "Text of tweet 002", "created_at": "2021-02-09T05:46:35.000Z", "optional_key": "content of optional additional key"}
...
{"id": 100, "text": "Text of tweet 100", "created_at": "2021-02-15T08:26:52.000Z", "optional_key": "content of optional additional key"}
```

Then, just run the following command to predict the emotions of each tweet:

```
python predict_emotions.py -I $INPUT_FILEPATH -O $OUTPUT_BASE_FILEPATH -L $LANG_CODE
```

where:
- `$INPUT_FILEPATH` (**required**): the path to the json line file with tweets to classify (with at least three keys: "id", "text", and "created_at").
- `$OUTPUT_BASE_FILEPATH`: the name of the base output filepath on which to base the name of output files.
- `$LANG_CODE` (default: `en`): the language code of the tweets. Choices are `en`, `it`, and `bg` (experimental).

As a result, you will obtain four output files (examples follow):
- `$OUTPUT_BASE_FILEPATH_annotated_raw.tsv`: a tab-separated file containing the original tweet in jsonl format on the first column, and the emotion values as dictionary in the second column;
- `$OUTPUT_BASE_FILEPATH_annotated.tsv`: a tab-separated file (with header) containing the date, preprocessed text, and emotion values for each tweet (one per line);
- `$OUTPUT_BASE_FILEPATH_stats_norm.tsv`: a tab-separated file (with header) containing normalized values per emotion class, grouped by date;
- `$OUTPUT_BASE_FILEPATH_stats.tsv`: a tab-separated file (with header) containing values per emotion class, grouped by date.

`$OUTPUT_BASE_FILEPATH_annotated_raw.tsv` example:
```
{"id": 001, "text": "Text of tweet 001", "created_at": "2021-02-08T02:06:18.000Z", "optional_key": "content of optional additional key"}	{'nrcDict_Anger': 0.0, 'nrcDict_Joy': 0.0, ..., 'nrcDict_Fear': 2.0}
{"id": 002, "text": "Text of tweet 002", "created_at": "2021-02-09T05:46:35.000Z", "optional_key": "content of optional additional key"}	{'nrcDict_Anger': 0.0, 'nrcDict_Joy': 3.0, ..., 'nrcDict_Fear': 0.0}
...
{"id": 100, "text": "Text of tweet 100", "created_at": "2021-02-15T08:26:52.000Z", "optional_key": "content of optional additional key"}	{'nrcDict_Anger': 3.0, 'nrcDict_Joy': 0.0, ..., 'nrcDict_Fear': 1.0}
```

`$OUTPUT_BASE_FILEPATH_annotated.tsv` example:
```
date	post_preprocessed	anger	anticipation	disgust	fear	joy	sadness	surprise	trust	valence	arousal	dominance	positive	negative
2021-02-08	preprocessed text of tweet 001	0.0	2.0	0.0	1.0	1.0	0.0	0.0	4.0	7.503	4.965	7.24	0.0	2.0	
2021-02-08	preprocessed text of tweet 001	0.0	0.0	0.0	0.0	4.0	1.0	0.0	2.0	7.503	1.002	1.15	3.0	1.0	
...
2021-02-18	preprocessed text of tweet 001	1.0	1.0	0.0	0.0	1.0	3.0	0.0	0.0	7.503	2.163	4.13	1.0	0.0	
```

`$OUTPUT_BASE_FILEPATH_stats_norm.tsv` example:
```
date	anger	anticipation	disgust	fear	joy	sadness	surprise	trust	valence	arousal	dominance	positive	negative
2021-10-01	0.7	1.1	0.4	1.0	0.7	0.6	0.3	1.9	5.53	4.32	5.36	1.9	1.8
...
```

`$OUTPUT_BASE_FILEPATH_stats.tsv` example:
```
date	anger	anticipation	disgust	fear	joy	sadness	surprise	trust	valence	arousal	dominance	positive	negative
2021-10-01	7.0	11.0	4.0	10.0	7.0	6.0	3.0	19.0	55.338	43.247	53.611	19.0	18.0
...
```
##### Convert data to Twitter Explorer
The Twitter Explorer app needs a conversion in the Twitter format. To do that just run
```
python converter.py -I $INPUT_FILEPATH > $OUTPUT_FILEPATH
```

#### Run Geolocation
```
python get_locations.py -I [JSONL FILE]
```

