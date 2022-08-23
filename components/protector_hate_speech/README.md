# Hate speech detection module


## Environment

Create an environment with your own preferred package manager. We used [python 3.8](https://www.python.org/downloads/release/python-380/) and dependencies listed in `requirements.txt`. If you use [conda](https://docs.conda.io/en/latest/), you can just run the following commands from the root of the project:

```
conda create --name religioushate python=3.8      # create the environment
conda activate religioushate                      # activate the environment
pip install --user -r requirements.txt            # install the required packages
```


## Training

The following command can be used to train a religious hate speech detection model in a desired language `$LANG` (i.e., one among `en` (English), `it` (Italian) or `bg` (Bulgarian)):

```
sh scripts/train-religioushate-$LANG.sh
```

The resulting model will be in `logs/religioushate.$LANG/$DATETIME/model.tar.gz`, where `$DATETIME` is the datetime of the training process.


## Prediction

The following command can be used to predict -- using one of the previously trained language-specific models -- religious hate speech on new data in a desired language `$LANG` (i.e., one among `en` (English), `it` (Italian) or `bg` (Bulgarian)):

```
python machamp/predict.py \
    $MODEL_FILEPATH \
    $INPUT_FILEPATH \
    $OUTPUT_FILEPATH \
    --device 0
```

where:
- `$MODEL_FILEPATH`: the filepath to the trained model `model.tar.gz`
- `$INPUT_FILEPATH`: the filepath to the `.tsv` file containing posts to classify (see below for format)
- `$OUTPUT_FILEPATH`: the filepath where to write the `.tsv` results (see below for format)
- `--device`: `0` for GPU 0, `-1` for CPU


### File format

Input and output files are both tab-separated and have the following form: `LABEL\tTEXT` (see `.tsv` files in `machamp/data/en/religion/train_1.tsv` for an example.

You can add other columns to the input file, the only important thing is that the text of the post must appear in the second column (index: 1). The first column is reserved to the label and is added when predicting, so it should be empty in the input file containing posts to classify (i.e., the one provided with `$INPUT_FILEPATH`).