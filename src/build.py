import os
import subprocess

from colorama import Fore, Style

from src._config import config, app_reference
from src.downloader import Downloader
from src.logger import Logger


class Build(object):
    def __init__(self, args):
        # Generate the build dir if it doesn't exist
        if not os.path.exists(config["dist_dir"]):
            os.mkdir(config["dist_dir"])

        # Check if the keystore exists
        if not os.path.exists(config["keystore_path"]):
            Logger().error(
                f"The keystore file does not exist at {config['keystore_path']}"
            )
            exit(1)

        # Check if app_name is valid
        if args.app_name not in app_reference:
            Logger().error(
                f"Invalid app name. Valid apps are: {', '.join(app_reference.keys())}"
            )
            exit(1)

        self.args = args
        self.check_java_version()
        self.download_files = Downloader().download_required()

    def runBuild(self):
        target_app = self.args.app_name

        input_apk_filepath = Downloader().download_apk(target_app)

        Logger().info(f"🔥 Running build for {target_app}:")

        # Run the build
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
                "-m",
                self.download_files["revanced-integrations"],
                "--keystore",
                config["keystore_path"],
            ],
            stdout=subprocess.PIPE,
        )

        output = process.stdout

        # Stream the output to the console
        for line in output:
            print(line.decode("utf-8"), end="")

        if not output:
            raise Exception(
                Fore.RED + "An error occurred while running the Java program"
            )

    def check_java_version(self):
        version = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT
        ).decode("utf-8")

        if "17" not in version:
            Logger().error("Java 17 is required to run the build.")
            exit(1)

        Logger().success(Fore.GREEN + "Java 17 is installed" + Style.RESET_ALL)
