"""Print MD5 checksums for the standalone shell scripts without creating files."""

import hashlib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "packages/shell"
    for filename in ("curtail-str.sh", "curtail-str.bat", "curtail-str.ps1"):
        checksum = hashlib.md5((source / filename).read_bytes(), usedforsecurity=False)
        print(f"{checksum.hexdigest()}  {filename}")


if __name__ == "__main__":
    main()
