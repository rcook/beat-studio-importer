from colorama import Fore, Style


def print_key_value(name: str, value: object) -> None:
    print(
        Fore.LIGHTBLUE_EX,
        name,
        ": ",
        Fore.LIGHTCYAN_EX,
        str(value),
        Style.RESET_ALL,
        sep="")
