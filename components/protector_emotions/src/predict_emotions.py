import argparse
import json
from tkinter.font import ITALIC
import requests
import spacy
import stanza
from .emotionscorer import *

from datetime import datetime


EMOTION_KEYS = ["nrcDict_Anger", "nrcDict_Anticipation", "nrcDict_Disgust", "nrcDict_Fear", "nrcDict_Joy", "nrcDict_Sadness", "nrcDict_Surprise", "nrcDict_Trust"]
VAD_KEYS = ["nrcVadDict_Valence", "nrcVadDict_Arousal", "nrcVadDict_Dominance"]
SENTIMENT_KEYS = ["nrcPosNegDict_Positive", "nrcPosNegDict_Negative"]
ALL_EMO_KEYS = EMOTION_KEYS + VAD_KEYS + SENTIMENT_KEYS
ALL_EMO_KEYS_CLEANED = [emotion.split("_")[1].lower() for emotion in ALL_EMO_KEYS]
OUTPUT_HEADER = ["date", "post_preprocessed"] + ALL_EMO_KEYS_CLEANED

def insert_emotions(tweet, data, social_media, language, local):
    t = json.loads(tweet)
    for k, v in data.items():
        if v == 0 or v == 1:
            data[k] = float(v)
        else:
            data[k] = float(2)
    if social_media == "yt":
        data["youtube_id"] = t["id"]
        json_body = [
            {
                "time": t["created_at"],
                "measurement": "youtube_emotions",
                "tags": {"language": language, "local": local},
                "fields": data,
            }
        ]
    else:
        data["tweet_id"] = t["id"]
        json_body = [
            {
                "time": t["created_at"],
                "measurement": "emotions",
                "tags": {"language": language, "local": local},
                "fields": data,
            }
        ]
    return str(json_body)


def annotate_emotions(input_filepath, lang_code, lemmatizer, social_media, local):
    results = []
    date_counter = dict()
    emotion_counter = dict()

    # output_base_filepath = path
    # Create output file where to store raw tweet information and emotion values
    # output_file_raw = open(output_base_filepath + "_annotated_raw.tsv", "w")

    # Create output file where to store preprocessed tweet information and emotion values
    # output_file = open(output_base_filepath + "_annotated.tsv", "w")
    # output_file.write("\t".join(OUTPUT_HEADER))
    # output_file.write("\n")

    # with open(input_filepath, "r") as f:
    for json_object in input_filepath:
        # Get the relevant information for the tweet
        json_dict = json.loads(json_object)
        raw_datetime = json_dict["created_at"]
        date = datetime.strftime(datetime.strptime(raw_datetime, "%a %b %d %H:%M:%S +0000 %Y"), "%Y-%m-%d")
        post = json_dict["text"]

        # Get preprocessed text and emotion results
        post = post.replace("\n", " ")
        post = post.replace("\t", " ")

        if lang_code == "bg":
            doc = lemmatizer(post)
            lemmasList = [word.lemma.lower() for word in doc.sentences[0].words]
            # wordList = [word.text for word in doc.sentences[0].tokens]
            post_preprocessed = " ".join([lemma for lemma in lemmasList])

        else:
            lemmas = lemmatizer(post)
            post_preprocessed = ""
            for i in range(len(lemmas)):
                if lemmas[i].lemma_ == "-PRON-":
                    post_preprocessed = post_preprocessed + lemmas[i].text + " "
                else:
                    post_preprocessed = post_preprocessed + lemmas[i].lemma_ + " "

        emotion_result = extractEmotions(lang_code, post_preprocessed)
        response = {}
        response["preprocessedText"] = post
        response["emotions"] = emotion_result
        
        # Store relevant information from the response
        post_preprocessed = response["preprocessedText"]
        emotions = response["emotions"]

        influx_data = insert_emotions(json_object, emotions, social_media, lang_code, local)
        results.append(influx_data)

        # Initialize date counters for normalization
        if date not in date_counter:
            date_counter[date] = 0
        date_counter[date] += 1

        # Initialize emotion counters with respect to dates
        if date not in emotion_counter:
            emotion_counter[date] = dict()

        # Print tweet information to the file(s)
        # output_file_raw.write(json_object.rstrip("\n") + "\t" + str(emotions) + "\n")
        # output_file.write(date + "\t" + post_preprocessed + "\t")

        # For each emotion, store information to the emotion dictionary and to the file
        # for emotion in ALL_EMO_KEYS:
        #     emotion_key = emotion.split("_")[1].lower()
        #     if emotion_key not in emotion_counter[date]:
        #         emotion_counter[date][emotion_key] = 0.0
        #     emotion_counter[date][emotion_key] += emotions[emotion]
        #     output_file.write(str(emotions[emotion]) + "\t")
        # output_file.write("\n")
    return results
    # output_file_raw.close()
    # output_file.close()

    # Create output file and store unnormalized statistics in it
    # output_file = open(output_base_filepath + "_stats.tsv", "w")
    # is_header = True
    # for date, emotions in emotion_counter.items():
    #     if is_header:
    #         output_file.write("date" + "\t")
    #         output_file.write("\t".join(emotions.keys()))
    #         output_file.write("\n")
    #         is_header = False
    #     output_file.write(date)
    #     for emotion, value in emotions.items():
    #         output_file.write("\t" + str(value))
    #     output_file.write("\n")
    # output_file.close()

    # Normalize statistics based on the number of total posts per date
    # for date, num_posts in date_counter.items():
    #     for emotion, value in emotion_counter[date].items():
    #         emotion_counter[date][emotion] = round(emotion_counter[date][emotion] / float(num_posts), 2)

    # Create output file and store normalized statistics in it
    # output_file = open(output_base_filepath + "_stats_norm.tsv", "w")
    # is_header = True
    # for date, emotions in emotion_counter.items():
    #     if is_header:
    #         output_file.write("date" + "\t")
    #         output_file.write("\t".join(emotions.keys()))
    #         output_file.write("\n")
    #         is_header = False
    #     output_file.write(date)
    #     for emotion, value in emotions.items():
    #         output_file.write("\t" + str(value))
    #     output_file.write("\n")
    # output_file.close()


def predict_emotions(input_file, lang_code, social_media, local):
    # Create emotion lexicons
    createNrcEmotionLexicons("components/protector_emotions/src/resources/emotionDictionaries/nrc_emotions")
    createNrcPositiveNegativeLexicons("components/protector_emotions/src/resources/emotionDictionaries/nrc_emotions")
    createNrcVadLexicon("components/protector_emotions/src/resources/emotionDictionaries/nrc_valence")

    if lang_code == "bg":
        stanza.download("bg")
        lemmatizer = stanza.Pipeline("bg", processors='tokenize,pos,lemma', use_gpu=False)
    else:
        lemmatizer_name = "it_core_news_lg" if lang_code == "it" else "en_core_web_lg"
        lemmatizer = spacy.load(lemmatizer_name, disable=['parser', 'ner'])

    return annotate_emotions(input_file, lang_code, lemmatizer, social_media, local)




# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-I", "--input_filepath", type=str, required=True, 
#         help="The path to the json line file with tweets to classify (with at least three keys: 'id', 'text', and 'created_at').")
#     parser.add_argument("-O", "--output_base_filepath", type=str, required=True, 
#         help="The name of the base output filepath on which to base the name of output files.")
#     parser.add_argument("-L", "--lang_code", type=str, required=False, default="en", 
#         help="The language code of the tweets. Choices: ['en', 'it', 'bg'].")
#     args = parser.parse_args()

#     # Create emotion lexicons
#     emotionscorer.createNrcEmotionLexicons("resources/emotionDictionaries/nrc_emotions")
#     emotionscorer.createNrcPositiveNegativeLexicons("resources/emotionDictionaries/nrc_emotions")
#     emotionscorer.createNrcVadLexicon("resources/emotionDictionaries/nrc_valence")

#     # Loading spacy or stanza model
#     # You need to download the models beforehand:
#     # python -m spacy download en_core_web_lg
#     # python -m spacy download it_core_news_lg
#     if args.lang_code == "bg":
#         stanza.download("bg")
#         lemmatizer = stanza.Pipeline("bg", processors='tokenize,pos,lemma', use_gpu=False)
#     else:
#         lemmatizer_name = "it_core_news_lg" if args.lang_code == "it" else "en_core_web_lg"
#         lemmatizer = spacy.load(lemmatizer_name, disable=['parser', 'ner'])

#     annotate_emotions(args.input_filepath, args.output_base_filepath, args.lang_code, lemmatizer)