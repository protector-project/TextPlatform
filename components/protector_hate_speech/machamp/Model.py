import os
import logging
import argparse
import tarfile
import copy
from pathlib import Path
from allennlp.common import Params
from allennlp.common.util import import_module_and_submodules
from machamp import util


# parser = argparse.ArgumentParser()
# parser.add_argument("archive", type=str, help="The archive file")
# parser.add_argument("input_file", type=str, help="The input file to predict")
# parser.add_argument("pred_file", type=str, help="The output prediction file")
# parser.add_argument("--dataset", default=None, type=str,
#                     help="name of the dataset, needed to know the word_idx/sent_idxs to read from")
# #parser.add_argument("--write_scores", default=None, type=str, # TODO
# #                    help="If set, evaluate the prediction and store it in the given file")
# parser.add_argument("--device", default=None, type=int, help="CUDA device number; set to -1 for CPU")
# parser.add_argument("--batch_size", default=None, type=int, help="The size of each prediction batch")
# parser.add_argument("--raw_text", action="store_true", help="Input raw sentences, one per line in the input file.")
# args = parser.parse_args()

import_module_and_submodules("machamp")

# archive_dir = Path(args.archive).resolve().parent

# if not os.path.isfile(archive_dir / "weights.th"):
#     with tarfile.open(args.archive) as tar:
#         tar.extractall(archive_dir)


# if args.device is not None: 
#     params['trainer']['cuda_device'] = args.device
# params['dataset_reader']['is_raw'] = args.raw_text

# if args.dataset is None and len(params['dataset_reader']['datasets']) > 1:
#     logger.error("please provide --dataset, because we currently don't support writing " +
#                  "tasks of multiple datasets in one run.\nOptions: " +
#                  str([dataset for dataset in params['dataset_reader']['datasets']]))
#     exit(1)

# if args.dataset not in params['dataset_reader']['datasets'] and args.dataset is not None:
#     logger.error("Non existing --dataset option specified, please pick one from: " + 
#                  str([dataset for dataset in params['dataset_reader']['datasets']]))
#     exit(1)

# if args.dataset:
#     datasets = copy.deepcopy(params['dataset_reader']['datasets'])
#     for iter_dataset in datasets:
#         if iter_dataset != args.dataset:
#             del params['dataset_reader']['datasets'][iter_dataset]


class Model:
  def __init__(self):
    """Custom logic that prepares model.
    - Reusable servers: your_loader downloads model from remote repository.
    - Non-Reusable servers: your_loader loads model from a file embedded in the image.
    """

  def predict(self, features, names=[], meta=[]):
    import tempfile
    print(features)
    tf_input = None
    tf_output = None
    try:
        # select model and extract
        
        if True:
            model_path = "/app/mlModels/en/weights.th"
            archive_dir = Path(model_path).resolve().parent
            if not os.path.isfile(archive_dir / "weights.th"):
                with tarfile.open(model_path) as tar:
                    tar.extractall(archive_dir)
            
            config_file = archive_dir / "config.json"

            params = Params.from_file(config_file)

            params['trainer']['cuda_device'] = -1
            params['dataset_reader']['is_raw'] = False


        # create temporary file
        tf_input = tempfile.NamedTemporaryFile()
        tf_output = tempfile.NamedTemporaryFile()
        with open(tf_input.name, 'w') as f:
            for i in features:
                f.write(str(i))
                f.write("\n")
        """Custom inference logic."""
        util.predict_model_with_archive("machamp_predictor", params, archive_dir, tf_input.name, tf_output.name,
                                    batch_size=None)
        
        with open(tf_output.name, "r") as f:
            return f.readlines()


    except Exception as e:
        print(e)
        return (e)
    finally:
        tf_input.close()
        tf_output.close()


# m = Model()
# print(m.predict("RELIGIOUS HATE\toioioioioi"))
