# Training.

# Variables declaration
declare -a PRETRAINED_MODELS=("roberta")
declare -a DATASETS=("religion")
declare -a SPLITS=("1")

for MODEL in "${PRETRAINED_MODELS[@]}"
do
    for DATASET in "${DATASETS[@]}"
    do
        for SPLIT in "${SPLITS[@]}"
        do
            python machamp/train.py \
                --dataset_config machamp/configs/$DATASET.en.$SPLIT.json \
                --parameters_config machamp/configs/params.$MODEL.json \
                --name religioushate.en \
                --device -0
        done
    done
done