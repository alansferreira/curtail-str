"""Build portable shell archives and SHA-256 checksums using the standard library."""

import hashlib
from pathlib import Path
import tarfile
import zipfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "packages/shell"
    destination = source / "dist"
    destination.mkdir(exist_ok=True)
    name = "abbrev-shell-0.1.0"
    files = ("abbrev.sh", "abbrev.bat", "abbrev.ps1", "README.md")
    archive = destination / f"{name}.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        for filename in files:
            info = output.gettarinfo(str(source / filename), arcname=f"{name}/{filename}")
            info.mode = 0o755 if filename.endswith(".sh") else 0o644
            with (source / filename).open("rb") as content:
                output.addfile(info, content)
    with zipfile.ZipFile(destination / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as output:
        for filename in files:
            data = (source / filename).read_bytes()
            if filename.endswith((".bat", ".ps1")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            output.writestr(f"{name}/{filename}", data)
    checksums = []
    for path in (archive, destination / f"{name}.zip"):
        checksums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")
        print(path)
    (destination / "SHA256SUMS").write_text("".join(checksums), encoding="ascii")


if __name__ == "__main__":
    main()
