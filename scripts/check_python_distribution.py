"""Install each supplied distribution in isolation and run the shared contract."""

from pathlib import Path
import subprocess
import sys
import tempfile
import venv


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: check_python_distribution.py DIST [DIST ...]")
    tests = Path(__file__).resolve().parents[1] / "packages/python/tests"
    for argument in sys.argv[1:]:
        distribution = Path(argument).resolve(strict=True)
        with tempfile.TemporaryDirectory(prefix="abbrev-python-") as directory:
            venv.create(directory, with_pip=False)
            executable = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
            python = Path(directory) / executable
            subprocess.run([str(python), "-m", "ensurepip", "--upgrade"], check=True)
            subprocess.run(
                [str(python), "-m", "pip", "install", "--no-deps", str(distribution)],
                check=True,
            )
            subprocess.run(
                [str(python), "-I", "-m", "unittest", "discover", "-s", str(tests), "-v"],
                cwd=directory,
                check=True,
            )
            subprocess.run(
                [str(python), "-I", "-c",
                 "from importlib.resources import files; "
                 "assert files('abbrev').joinpath('py.typed').is_file()"],
                cwd=directory,
                check=True,
            )


if __name__ == "__main__":
    main()
