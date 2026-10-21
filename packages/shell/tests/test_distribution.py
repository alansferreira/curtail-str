from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from threading import Thread
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[3]
DIST = ROOT / "packages/shell/dist"
NAME = "abbrev-shell-0.1.0"
FILES = {"abbrev.sh", "abbrev.bat", "abbrev.ps1", "README.md"}


class DistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "scripts/package_shell.py")], check=True)

    def test_archives_and_checksums(self):
        for line in (DIST / "SHA256SUMS").read_text(encoding="ascii").splitlines():
            expected, filename = line.split("  ")
            self.assertEqual(hashlib.sha256((DIST / filename).read_bytes()).hexdigest(), expected)
        with tarfile.open(DIST / f"{NAME}.tar.gz") as archive:
            self.assertEqual(set(archive.getnames()), {f"{NAME}/{name}" for name in FILES})
            self.assertEqual(archive.getmember(f"{NAME}/abbrev.sh").mode, 0o755)
        with zipfile.ZipFile(DIST / f"{NAME}.zip") as archive:
            self.assertEqual(set(archive.namelist()), {f"{NAME}/{name}" for name in FILES})
            for name in ("abbrev.bat", "abbrev.ps1"):
                data = archive.read(f"{NAME}/{name}")
                self.assertIn(b"\r\n", data)
                self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

    @unittest.skipUnless(os.name != "nt" and shutil.which("curl"), "Requires POSIX and curl")
    def test_http_download_and_standalone_execution(self):
        handler = partial(SimpleHTTPRequestHandler, directory=str(DIST))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/{NAME}.tar.gz"
            result = subprocess.run(["curl", "-fsSL", url], capture_output=True, check=True)
            self.assertEqual(result.stdout, (DIST / f"{NAME}.tar.gz").read_bytes())
            with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
                with tempfile.TemporaryDirectory(prefix="abbrev-shell-") as directory:
                    script = Path(directory) / "abbrev.sh"
                    with archive.extractfile(f"{NAME}/abbrev.sh") as content:
                        script.write_bytes(content.read())
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
