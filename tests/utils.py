import platform
import random
import string
import subprocess
from pathlib import Path

_MAX_RETRIES = 10
GENERATED_STRING_CHARACTERS = string.ascii_lowercase + " "


def possible_to_run_exe() -> bool:
    if platform.system() == "Windows":
        return True

    try:
        subprocess.run(["wine"], shell=False, check=False)
        return True
    except FileNotFoundError:
        return False


def get_exe_stdout(exe_path: Path) -> set[str]:
    if platform.system() == "Windows":
        result = subprocess.check_output([exe_path], shell=False)  # noqa: S603
    else:
        result = subprocess.check_output(["wine", exe_path], shell=False)  # noqa: S603, S607

    return set(result.decode().splitlines())


def get_random_string(length: int, not_equals: str | None = None) -> str:
    counter = 0
    while True:
        generated_string = "".join(random.choices(GENERATED_STRING_CHARACTERS, k=length))
        if not_equals is None or generated_string != not_equals:
            return generated_string

        counter += 1
        if counter >= _MAX_RETRIES:
            raise ValueError("Infinite loop")
