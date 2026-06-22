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
    env["STUI_CUSTOM_PROJECT_DIR"] = str(tmp_path / "custom-project")

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
    assert (tmp_path / "custom-project" / "helper.py").exists()
    assert (tmp_path / "custom-project" / "app.py").exists()
    assert (tmp_path / "custom-project" / "selftest-result.json").exists()
    assert (tmp_path / "custom-project" / "check-result.json").exists()
