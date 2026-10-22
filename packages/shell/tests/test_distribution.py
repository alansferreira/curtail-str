from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/shell"
FILES = ("curtail-str.sh", "curtail-str.bat", "curtail-str.ps1")


class DistributionTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="curtail-str-checksums-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "scripts").mkdir()
        self.package = self.root / "packages/shell"
        self.package.mkdir(parents=True)
        self.command = self.root / "scripts/package_shell.py"
        shutil.copyfile(ROOT / "scripts/package_shell.py", self.command)
        for filename in FILES:
            shutil.copyfile(PACKAGE / filename, self.package / filename)

    def run_checksums(self):
        return subprocess.run(
            [sys.executable, str(self.command)],
            cwd=self.package, capture_output=True, text=True, check=True,
        )

    def test_script_checksums_without_filesystem_changes(self):
        before = {
            path.relative_to(self.root): path.read_bytes() if path.is_file() else None
            for path in self.root.rglob("*")
        }
        result = self.run_checksums()
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.splitlines(), [
            f"{hashlib.md5((self.package / name).read_bytes(), usedforsecurity=False).hexdigest()}  {name}"
            for name in FILES
        ])
        after = {
            path.relative_to(self.root): path.read_bytes() if path.is_file() else None
            for path in self.root.rglob("*")
        }
        self.assertEqual(before, after)

    def test_reproducible_checksums(self):
        self.assertEqual(self.run_checksums().stdout, self.run_checksums().stdout)

    def test_original_line_endings(self):
        for filename in FILES:
            (self.package / filename).write_bytes(b"abc\r\n")
        self.assertEqual(
            self.run_checksums().stdout.splitlines(),
            [f"c13b6afecf97ea6b38d21a8f5167fa1e  {name}" for name in FILES],
        )

    def test_missing_script_fails(self):
        (self.package / FILES[0]).unlink()
        result = subprocess.run(
            [sys.executable, str(self.command)], capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("FileNotFoundError", result.stderr)

    @unittest.skipUnless(os.name != "nt" and shutil.which("curl"), "Requires POSIX and curl")
    def test_http_download_and_standalone_execution(self):
        handler = partial(SimpleHTTPRequestHandler, directory=str(PACKAGE))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/curtail-str.sh"
            result = subprocess.run(["curl", "-fsSL", url], capture_output=True, check=True)
            self.assertEqual(result.stdout, (PACKAGE / "curtail-str.sh").read_bytes())
            with tempfile.TemporaryDirectory(prefix="curtail-str-shell-") as directory:
                script = Path(directory) / "curtail-str.sh"
                script.write_bytes(result.stdout)
                output = subprocess.run(
                    ["sh", str(script), "codigo-do-cliente-ativo-no-estoque"],
                    cwd=directory, capture_output=True, text=True, check=True,
                )
                self.assertEqual(output.stdout, "cdg-clnt-atv-estq\n")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
