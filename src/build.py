import os
import subprocess

from src._config import config
from src.downloader import Downloader
from src.logger import Logger
from src.validation import Validation


class Build(object):
    def __init__(self, args):
        # Generate the build dir if it doesn't exist
        if not os.path.exists(config["dist_dir"]):
            os.mkdir(config["dist_dir"])

        Validation().check_keystore()
        Validation().check_app_name(args.app_name)

        self.args = args
        self.check_java_version()
        self.download_files = Downloader().download_required()

        # Validate the patches from exclude_patches
        if self.args.exclude_patches:
            Validation().check_patch_from_args(self.args.exclude_patches)

    def runBuild(self):
        target_app = self.args.app_name.lower().strip()

        input_apk_filepath = Downloader().download_apk(target_app)

        Logger().info(f"🔥 Running build for {target_app}:")

        # Run the build command
        process = subprocess.Popen(
            [
                "java",
                "-jar",
                self.download_files["revanced-cli"],
                "--bundle",
                self.download_files["revanced-patches"],
                "--apk",
                input_apk_filepath,
                "--out",
                f"./{config['dist_dir']}/output-{target_app}.apk",
                "--merge",
                self.download_files["revanced-integrations"],
                "--keystore",
                config["keystore_path"],
            ]
            + sum(
                [
                    ["--exclude", s.strip()]
                    for s in self.args.exclude_patches.split(",")
                ],
                [],
            ),
            stdout=subprocess.PIPE,
        )

        output = process.stdout

        # Stream the output to the console
        for line in output:
            print(line.decode("utf-8"), end="")

        if not output:
            Logger().error("An error occurred while running the Java program")
            exit(1)

        output_path = f"./revanced-cache/output-{target_app}_signed.apk"

        # Check if the output file exists
        if not os.path.exists(output_path):
            Logger().error(f"An error occurred while building {target_app}")
            exit(1)

        Logger().success(f"Build completed successfully: {output_path}")

    def check_java_version(self):
        version = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT
        ).decode("utf-8")

        if "17" not in version:
            Logger().error("Java 17 is required to run the build.")
            exit(1)

        Logger().success("Java 17 is installed")
