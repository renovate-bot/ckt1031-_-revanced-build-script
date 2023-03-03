from colorama import Fore, Style


class Logger:
    def success(self, message):
        print(Fore.GREEN + f"✅ {message}" + Style.RESET_ALL)

    def info(self, message):
        print(Fore.BLUE + f"{message}" + Style.RESET_ALL)

    def error(self, message):
        print(Fore.RED + f"❌ {message}" + Style.RESET_ALL)

    def warning(self, message):
        print(Fore.YELLOW + f"⚠️ {message}" + Style.RESET_ALL)

    def log(self, message):
        print(message)
