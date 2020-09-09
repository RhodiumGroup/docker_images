from pathlib import Path
import json
import yaml
import os

cred_files = Path("/home/jovyan/service-account-credentials").glob("*.json")

out_file = Path("/opt/conda/etc/dask/gateway.yaml")
out_file.parent.mkdir(exist_ok=True, parents=True)

# get tokens
tokens = {}
for fpath in cred_files:
    bucket = fpath.stem
    with open(fpath, "r") as file:
        tokens[bucket] = json.load(file)

# get image names
scheduler_image = os.environ["JUPYTER_IMAGE_SPEC"].replace("/notebook:","/scheduler:")
worker_image = os.environ["JUPYTER_IMAGE_SPEC"].replace("/notebook:","/worker:")

# create config dict
config = {
    "gateway": {
        "cluster": {
            "options": {
                "gcsfuse_tokens": json.dumps(tokens).replace("{","{{").replace("}","}}"),
                "scheduler_image": scheduler_image,
                "worker_image": worker_image
            }
        }
    }
}

with open(out_file, "w") as fout:
    yaml.safe_dump(config, fout)