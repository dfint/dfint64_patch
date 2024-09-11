from pathlib import Path

import pytest

tests_dir = Path(__file__).parent


@pytest.fixture
def exe_file_path() -> Path:
    return tests_dir / "test64.exe"
