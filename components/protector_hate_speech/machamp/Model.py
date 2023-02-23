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
from downloader import download_from_config

import_module_and_submodules("machamp")

class Model:
  def __init__(self):
    """Custom logic that prepares model.
    - Reusable servers: your_loader downloads model from remote repository.
    - Non-Reusable servers: your_loader loads model from a file embedded in the image.
    """
    self.config = os.environ.get("CONFIG_MODEL_PATH")
    self.ready = False
    self.model_path = self.config["path"]
    if self.config == None:
        print(f"Path value is None in the environment")
        return
    else:
        self.load()
    
  def load(self):
    download_from_config(self.config)
    self.archive_dir = Path(self.model_path).resolve().parent
    if not os.path.isfile(self.archive_dir / "weights.th"):
        with tarfile.open(self.model_path) as tar:
            tar.extractall(self.archive_dir)
    
    config_file = self.archive_dir / "config.json"

    self.params = Params.from_file(config_file)

    self.params['trainer']['cuda_device'] = -1
    self.params['dataset_reader']['is_raw'] = False

  def predict(self, features, names=[], meta=[]):
    import tempfile
    print(features)
    tf_input = None
    tf_output = None
    try:
        # select model and extract
        
        if not self.ready:
            self.load()


        # create temporary file
        tf_input = tempfile.NamedTemporaryFile()
        tf_output = tempfile.NamedTemporaryFile()
        with open(tf_input.name, 'w') as f:
            for i in features:
                f.write(str(i))
                f.write("\n")
        """Custom inference logic."""
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

  def download_file(self,url,path: str = None):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    if path != None:
        local_filename = path + '/' + local_filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
            print(f"File downloaded in : {local_filename}")
    return local_filename

m = Model()
#print(m.predict("RELIGIOUS HATE\toioioioioi"))
