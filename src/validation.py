import json
import os

from loguru import logger

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
                # Check if the patch is valid
                if _patch.strip() not in [p["name"] for p in patches]:
                    logger.error(f"Invalid patch name: {_patch}")

                    # Send the available patches
                    logger.error(
                        f"Available patches: {', '.join([p['name'] for p in patches])}"
                    )
                    exit(1)

    def check_keystore(self):
        # Check if the keystore exists
        if not os.path.exists(config["keystore_path"]):
            logger.error(
                f"The keystore file does not exist at {config['keystore_path']}"
            )
            exit(1)

    def check_app_name(self, name: str):
        # Check if app_name is valid
        if name.lower().strip() not in app_reference:
            logger.error(
                f"Invalid app name. Valid apps are: {', '.join(app_reference.keys())}"
            )
            exit(1)
