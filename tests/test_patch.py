import shutil
import tempfile
from pathlib import Path

import pytest

from dfint64_patch.patching import patch

from .utils import get_exe_stdout, get_random_string, possible_to_run_exe


@pytest.mark.skipif(not possible_to_run_exe(), reason="Impossible to run exe file")
def test_patch_same_length(exe_file_path: Path):
    strings = set(get_exe_stdout(exe_file_path))
    string = next(iter(strings))
    translation = get_random_string(length=len(string), not_equals=string)
    dictionary = {string: translation}

    patched_exe = Path(tempfile.gettempdir()) / "test.exe"
    shutil.copy(exe_file_path, patched_exe)

    patch(patched_exe, list(dictionary.items()), encoding="latin")
    new_strings = set(get_exe_stdout(patched_exe))

    assert string not in new_strings
    assert translation in new_strings
    assert new_strings - {translation} == strings - {string}
