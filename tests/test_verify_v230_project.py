from pathlib import Path

import pytest

from scripts.verify_v230_project import _exclusive_workdir


def test_v230_validator_refuses_existing_or_symlinked_workdirs(
    tmp_path: Path,
) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(RuntimeError, match="refusing existing"):
        _exclusive_workdir(existing)

    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(RuntimeError, match="refusing existing"):
        _exclusive_workdir(link)
