import json
import os
from src.logger import Logger
from src._config import app_reference, config


class Validation:
    # Validate the patches from exclude_patches
    def check_patch_from_args(self, args_patch):
        # Read from the patches.json file
        with open("./" + config["dist_dir"] + "/patches.json", "r") as f:
            # [{ "name": "patch_description" }}]
            patches = json.load(f)

            # Check if the patches are valid
            for _patch in args_patch.split(","):
                if _patch.strip() not in patches:
                    Logger().error(f"Invalid patch: {_patch.strip()}")

                    # Send the available patches
                    Logger().log(
                        f"Available patches: {', '.join([p['name'] for p in patches])}"
                    )

                    exit(1)

    def check_keystore(self):
        # Check if the keystore exists
        if not os.path.exists(config["keystore_path"]):
            Logger().error(
                f"The keystore file does not exist at {config['keystore_path']}"
            )
            exit(1)

    def check_app_name(self, name: str):
        # Check if app_name is valid
        if name.lower().strip() not in app_reference:
            Logger().error(
                f"Invalid app name. Valid apps are: {', '.join(app_reference.keys())}"
            )
            exit(1)
