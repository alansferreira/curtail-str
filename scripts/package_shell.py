"""Build portable shell archives and SHA-256 checksums using the standard library."""

import hashlib
import gzip
import io
from pathlib import Path
import tarfile
import zipfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "packages/shell"
    destination = source / "dist"
    destination.mkdir(exist_ok=True)
    version = (root / "VERSION").read_text(encoding="ascii").strip()
    name = f"curtail-str-shell-{version}"
    files = ("curtail-str.sh", "curtail-str.bat", "curtail-str.ps1", "README.md")
    archive = destination / f"{name}.tar.gz"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as output:
        for filename in files:
            info = output.gettarinfo(str(source / filename), arcname=f"{name}/{filename}")
            info.mode = 0o755 if filename.endswith(".sh") else 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            with (source / filename).open("rb") as content:
                output.addfile(info, content)
        license_data = (root / "LICENSE").read_bytes()
        info = tarfile.TarInfo(f"{name}/LICENSE")
        info.size = len(license_data)
        info.mode = 0o644
        output.addfile(info, io.BytesIO(license_data))
    with archive.open("wb") as content:
        with gzip.GzipFile(fileobj=content, mode="wb", filename="", mtime=0) as output:
            output.write(buffer.getvalue())
    with zipfile.ZipFile(destination / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as output:
        for filename in (*files, "LICENSE"):
            path = root / "LICENSE" if filename == "LICENSE" else source / filename
            data = path.read_bytes()
            if filename.endswith((".bat", ".ps1")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            info = zipfile.ZipInfo(f"{name}/{filename}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100755 if filename.endswith(".sh") else 0o100644) << 16
            output.writestr(info, data)
    checksums = []
    for path in (archive, destination / f"{name}.zip"):
        checksums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")
        print(path)
    (destination / "SHA256SUMS").write_text("".join(checksums), encoding="ascii")


if __name__ == "__main__":
    main()
