from __future__ import annotations

from scripts import check_release_version


def test_release_version_metadata_matches() -> None:
    assert check_release_version.check_release_version() == []


def test_release_version_tag_must_match_project_version() -> None:
    errors = check_release_version.check_release_version("--not-a-tag")
    assert errors == []

    errors = check_release_version.check_release_version("v0.0.0")
    assert len(errors) == 1
    assert "does not match project version" in errors[0]
