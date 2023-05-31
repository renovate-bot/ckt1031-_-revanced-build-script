import argparse

from src.build import Build


def main():
    parser = argparse.ArgumentParser("revanced_build")

    # Target build app
    parser.add_argument("app_name", help="Target build app", type=str)

    # Exclude Patches: patch1,patch2,patch3
    parser.add_argument(
        "--exclude-patches",
        help="Exclude patches from build",
        type=str,
        default="none",
    )

    args = parser.parse_args()

    build = Build(args)

    build.run_build()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)
