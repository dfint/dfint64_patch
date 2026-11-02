import platform
import random
import shutil
import string
import subprocess
from pathlib import Path

_MAX_RETRIES = 10
GENERATED_STRING_CHARACTERS = string.ascii_lowercase


def possible_to_run_exe() -> bool:
    if platform.system() == "Windows":
        return True

    return shutil.which("wine") is not None


def get_exe_stdout(exe_path: Path) -> list[str]:
    if platform.system() == "Windows":
        result = subprocess.check_output([exe_path], shell=False)  # noqa: S603
    else:
        result = subprocess.check_output(["wine", exe_path], shell=False)  # noqa: S603, S607

    return list(result.decode().splitlines())


def get_random_word(length: int, not_equals: str | None = None) -> str:
    counter = 0
    while True:
        generated_string = "".join(random.choices(GENERATED_STRING_CHARACTERS, k=length))
        if not_equals is None or generated_string != not_equals:
            return generated_string

        counter += 1
        if counter >= _MAX_RETRIES:
            msg = "Infinite loop"
            raise ValueError(msg)


def get_random_string(length: int, not_equals: str | None = None) -> str:
    if length == 0:
        if not_equals is None or not_equals != "":
            return ""
        msg = "Infinite loop"
        raise ValueError(msg)

    counter = 0
    while True:
        words = []
        generated_length = 0
        while generated_length <= length:
            word = get_random_word(random.randint(1, length))
            words.append(word)
            generated_length += len(word)
            if len(words) > 1:
                generated_length += 1

        generated_string = " ".join(words)[:length]
        if generated_string.endswith(" "):
            continue

        if not_equals is None or generated_string != not_equals:
            return generated_string

        counter += 1
        if counter >= _MAX_RETRIES:
            msg = "Infinite loop"
            raise ValueError(msg)
