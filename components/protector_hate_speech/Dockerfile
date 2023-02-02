FROM nvcr.io/nvidia/pytorch:21.06-py3

COPY . /app/
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 5000
# Port for REST
EXPOSE 9000

# Define environment variables
ENV MODEL_NAME Model
ENV SERVICE_TYPE MODEL

# Changing folder to default user
RUN chown -R 8888 /app

WORKDIR /app/machamp/

RUN python Model.py

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE