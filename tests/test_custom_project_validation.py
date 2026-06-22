import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_verify_custom_project_script_runs_from_external_directory(
    tmp_path: Path,
) -> None:
    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
    )
    python = venv_dir / "bin" / "python"
    subprocess.run(
        [str(python), "-m", "pip", "install", "-e", str(ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    env = os.environ.copy()
    env["PYTHON"] = str(python)
    project_dir = tmp_path / "custom project with spaces"
    env["STUI_CUSTOM_PROJECT_DIR"] = str(project_dir)

    result = subprocess.run(
        [str(ROOT / "scripts" / "verify_custom_project.sh")],
        cwd="/tmp",
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "custom project validation passed:" in result.stdout
    assert (project_dir / "my_project" / "data.py").exists()
    assert (project_dir / "app.py").exists()
    assert (project_dir / "selftest-result.json").exists()
    assert (project_dir / "check-result.json").exists()

    selftest_payload = json.loads(
        (project_dir / "selftest-result.json").read_text(encoding="utf-8")
    )
    check_payload = json.loads(
        (project_dir / "check-result.json").read_text(encoding="utf-8")
    )
    assert selftest_payload["ok"] is True
    assert selftest_payload["strict"] is True
    assert check_payload["ok"] is True
    assert check_payload["strict"] is True
    assert check_payload["summary"]["warning_count"] == 0
