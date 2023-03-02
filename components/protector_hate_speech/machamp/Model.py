import os
import logging
import argparse
import tarfile
import seldon_core
import copy
from pathlib import Path
from allennlp.common import Params
from allennlp.common.util import import_module_and_submodules
from machamp import util
import requests
from downloader import download_from_config,obj_from_json,obj_from_json

import_module_and_submodules("machamp")

class Model:
  def __init__(self):
    """Custom logic that prepares model.
    - Reusable servers: your_loader downloads model from remote repository.
    - Non-Reusable servers: your_loader loads model from a file embedded in the image.
    """
    self.config = obj_from_json(os.environ.get("CONFIG_MODEL_PATH"))
    CACHE_ROOT = Path(os.getenv("ALLENNLP_CACHE_ROOT", Path.home() / ".allennlp"))
    print(CACHE_ROOT)
    self.ready = False
    self.model_path = self.config["path"]
    if self.config == None:
        print(f"CONFIG_MODEL_PATH is None in the environment")
        return
    else:
        self.set_with_load()
    
  def set_with_load(self):
    download_from_config(self.config)
    self.archive_dir = Path(self.model_path).resolve().parent
    if not os.path.isfile(self.archive_dir / "weights.th"):
        with tarfile.open(self.model_path) as tar:
            tar.extractall(self.archive_dir)
    
    config_file = self.archive_dir / "config.json"

    self.params = Params.from_file(config_file)

    self.params['trainer']['cuda_device'] = -1
    self.params['dataset_reader']['is_raw'] = False
    self.ready = True
    print("####################### Creating done #############################")

  def predict(self, features, names=[], meta=[]):
    import tempfile
    print(f"################################### {features}###################################################")
    tf_input = None
    tf_output = None
    try:
        if not self.ready:
           pass
            # self.load()
        # create temporary file
        tf_input = tempfile.NamedTemporaryFile()
        tf_output = tempfile.NamedTemporaryFile()
        with open(tf_input.name, 'w') as f:
            for i in features:
                f.write(str(i))
                f.write("\n")
        """Custom inference logic."""
        with open(tf_input.name, "r") as f:
            print('READING LINGES:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ',f.readlines())
        util.predict_model_with_archive("machamp_predictor", self.params, self.archive_dir, tf_input.name, tf_output.name,
                                    batch_size=None)
        
        with open(tf_output.name, "r") as f:
            return f.readlines()


    except Exception as e:
        print(e)
        return (e)
    finally:
        tf_input.close()
        tf_output.close()

#m = Model()
#print(m.predict("RELIGIOUS HATE\toioioioioi"))