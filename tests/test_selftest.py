from pathlib import Path

from song_dissect.selftest import run_selftest


def test_selftest(tmp_path: Path) -> None:
    assert run_selftest(tmp_path / "selftest")
