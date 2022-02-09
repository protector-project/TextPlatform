FROM nvcr.io/nvidia/pytorch:21.06-py3

COPY requirements.txt /app/requirements.txt
COPY predict_hate.py /app/predict_hate.py
COPY predict_emotions.py /app/predict_emotions.py
COPY InfluxClient.py /app/InfluxClient.py
COPY . /app/

WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm