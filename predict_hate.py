import argparse
import json
import os
import re
from html import unescape

import emoji
import numpy as np
import spacy
import torch
import wordsegment as ws
from spacy.matcher import Matcher
from transformers import (
    BertForSequenceClassification,
    BertTokenizerFast,
    Trainer,
    TrainingArguments,
)
from InfluxClient import InfluxClient

ws.load()  # load vocab for word segmentation

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class HateDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def regex_match_segmentation(match):
    return " ".join(ws.segment(match.group(0)))


def clean_text(text):
    # convert HTML codes
    text = unescape(text)

    # lowercase text
    text = text.lower()

    # replace mentions, URLs and emojis with special token
    text = re.sub(r"@[A-Za-z0-9_-]+", "[USER]", text)
    text = re.sub(r"http\S+", "[URL]", text)
    text = "".join(
        " [EMOJI] " if (char in emoji.UNICODE_EMOJI) else char for char in text
    ).strip()

    # find and split hashtags into words
    text = re.sub(r"#[A-Za-z0-9]+", regex_match_segmentation, text)

    # remove punctuation at beginning of string (quirk in Davidson data)
    text = text.lstrip("!")

    # remove newline and tab characters
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    return text


def replace_word(doc):
    replacement = "RELTERM"
    doc = nlp(doc)
    masked_doc = doc
    matches = matcher(doc)
    for match_id, start, end in matches:
        if (end - 1) < len(masked_doc):
            prev_whitespace = " " if masked_doc[start - 1].whitespace_ else ""
            succ_whitespace = " " if masked_doc[end - 1].whitespace_ else ""
        else:
            prev_whitespace = " "
            succ_whitespace = " "
        masked_doc = nlp.make_doc(
            masked_doc[:start].text
            + prev_whitespace
            + f"{replacement}"
            + succ_whitespace
            + masked_doc[end:].text
        )

    # print(masked_doc.text)
    return masked_doc.text


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-I",
    "--input_filepath",
    type=str,
    required=True,
    help="The path to the json line file with tweets to classify (with at least two keys: 'id' and 'text').",
)
parser.add_argument(
    "-DH",
    "--database_host",
    type=str,
    required=True,
    help="IP address of the database",
)
parser.add_argument(
    "-DP",
    "--database_port",
    type=str,
    required=True,
    help="Port number of the database",
)
parser.add_argument(
    "-DN",
    "--database_name",
    type=str,
    required=True,
    help="Name of the Database",
)
args = parser.parse_args()

i = InfluxClient(
        host=args.database_host,
        port=int(args.database_port),
        database=args.database_name,
    )
try:
    i.createConnection()
    i.ping()
except Exception as e:
    print(e) 
    exit()

# Load spacy model
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# English query terms
religion_c = ["christianity"]
adherent_c = ["christian", "christians"]  # "christian" added
scripture_c = ["bible", "old testament", "new testament"]
branch_and_adherent_c = [
    "catholicity",
    "catholicism",
    "catholic church",
    "protestantism",
    "eastern orthodox church",
    "orthodox catholic church",
    "catholic",
    "catholics",
    "protestant",
    "protestants",
    "orthodox",
    "orthodoxes",
]
religion_i = ["islam"]
adherent_i = ["muslim", "muslims", "moslem", "moslems", "islamic", "islamics"]
scripture_i = ["quran", "qur'an", "koran", "sunnah", "hadith", "athar"]
branch_and_adherent_i = [
    "sunni",
    "sunnism",
    "shia",
    "shi'a",
    "shiism",
    "shi'ism",
    "sunnis",
    "sunnite",
    "sunnites",
    "shias",
    "shi'as",
    "shiite",
    "shi'ite",
    "shiites",
    "shi'ites",
]
religion_j = ["judaism"]
adherent_j = ["jew", "jews", "jewish", "jewishes", "jewry", "jewries"]
scripture_j = ["tanach", "hebrew bible", "torah", "midrash", "talmud"]
branch_and_adherent_j = [
    "rabbanite",
    "rabbinic",
    "rabbinism",
    "rabbinicism",
    "karaite",
    "qaraite",
    "karaism",
    "qaraism",
    "rabbanites",
    "rabbi",
    "rabbis",
    "rabbinist",
    "rabbinists",
    "rabbinicist",
    "rabbinicists",
    "karaites",
    "qaraites",
]

# Build the comprehensive lexicon
lexicon = (
    religion_c
    + adherent_c
    + scripture_c
    + branch_and_adherent_c
    + religion_i
    + adherent_i
    + scripture_i
    + branch_and_adherent_i
    + religion_j
    + adherent_j
    + scripture_j
    + branch_and_adherent_j
)
# print(lexicon)

# Define pattern for matching the lexicon terms
pattern = [{"LOWER": {"IN": lexicon}}]
matcher.add("ReligiousTerm", [pattern])

texts = []
hate_labels = []

# Open the jsonl input file, read, clean, mask, and store preprocessed texts
with open(args.input_filepath, "r") as f:
    for json_object in f:
        json_dict = json.loads(json_object)
        post = json_dict["text"]
        post = clean_text(post)
        # post = replace_word(post)
        texts.append(post)
        hate_labels.append(0)  # dummy label
# print(texts[:10])
# print(hate_labels[:10])

# Import tokenizer (which includes custom special tokens for URLs, mentions and emojis), and tokenize text series
tokenizer = BertTokenizerFast.from_pretrained("./model/BERT_f18")
hate_encodings = tokenizer(texts, truncation=True, padding=True)

# Write it as PyTorch dataset
hate_dataset = HateDataset(hate_encodings, hate_labels)

# Load the fine-tuned model
models = {}
for dataset in ["f18"]:
    models[
        "{}_weighted".format(dataset)
    ] = BertForSequenceClassification.from_pretrained(
        "./model/BERT_f18".format(dataset)
    )

# Instantiate trainer objects for each model (already fine-tuned so no longer necessary to specify training and eval data)
# output directory is redundant because there is no further training but needs to be specified anyway
trainer = {}
for model in models:
    trainer[model] = Trainer(
        model=models[model],
        args=TrainingArguments(
            output_dir="./model/BERT_f18/test".format(model),
            per_device_eval_batch_size=64,
        ),
    )

# Apply the model to the data
results = {}
for model in trainer:
    results[model] = trainer[model].predict(hate_dataset)

hateful_indices = []
for model in trainer:
    index = 0
    for row in results[model][0]:
        label = int(np.argmax(row))
        if label == 1:
            hateful_indices.append(index)
        index += 1
# print(len(hateful_indices), "/", len(results[model][0]), "have been found")
# print(len(hateful_indices) / len(results[model][0]) * 100, "%")

# Print the results

line_counter = 0
with open(args.input_filepath, "r") as input_file:
    for line in input_file:
        try:
            if line_counter in hateful_indices:
                # print(line.rstrip() + "\thate")
                tweet = str(line.replace("\n", ""))
                i.insert_tweet(tweet, 1)
            else:
                # print(line.rstrip() + "\tnot-hate")
                tweet = str(line.replace("\n", ""))
                i.insert_tweet(tweet, 0)
        except Exception as e:
            print(e)
        line_counter += 1
