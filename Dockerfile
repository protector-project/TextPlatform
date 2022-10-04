FROM nvcr.io/nvidia/pytorch:22.08-py3

COPY . /app/
RUN rm -rf /opt/pytorch  # remove 1.2GB dir

ARG DEBIAN_FRONTEND=noninteractive

# Install linux packages
RUN apt update && apt install --no-install-recommends -y tzdata ffmpeg libsm6 libxext6joao nao faria isso, vdd pal
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN python -m spacy download en_core_web_lg
RUN python -m spacy download it_core_news_lg
