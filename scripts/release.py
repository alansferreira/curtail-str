"""Shared-version maintenance and explicit registry publication."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/alansferreira/curtail-str"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
VERSION_PATTERN = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def run(*args: str, cwd: Path | None = None, capture: bool = False) -> str:
    result = subprocess.run(
        args, cwd=cwd or ROOT, check=True, text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else ""


def parse_version(value: str) -> tuple[int, int, int]:
    if not VERSION_PATTERN.fullmatch(value):
        raise ValueError("Version must be stable SemVer X.Y.Z without leading zeros")
    return tuple(int(component) for component in value.split("."))


def current_version() -> str:
    value = (ROOT / "VERSION").read_text(encoding="ascii").strip()
    parse_version(value)
    return value


def check_versions() -> str:
    version = current_version()
    node = json.loads((ROOT / "packages/node/package.json").read_text())
    lock = json.loads((ROOT / "packages/node/package-lock.json").read_text())
    python = tomllib.loads((ROOT / "packages/python/pyproject.toml").read_text())
    java = ET.parse(ROOT / "packages/java/pom.xml").getroot()
    versions = {
        "node": node["version"], "npm lock": lock["version"],
        "npm root package": lock["packages"][""]["version"],
        "python": python["project"]["version"],
        "java": java.findtext("m:version", namespaces=NS),
    }
    for name, value in versions.items():
        if value != version:
            raise ValueError(f"{name} version {value!r} does not match VERSION {version}")
    license_text = (ROOT / "LICENSE").read_bytes()
    for package in ("node", "python", "go", "java"):
        if (ROOT / f"packages/{package}/LICENSE").read_bytes() != license_text:
            raise ValueError(f"{package}/LICENSE does not match the root license")
    return version


def next_version(current: str, part: str, explicit: str | None = None) -> str:
    numbers = list(parse_version(current))
    if explicit is not None:
        if parse_version(explicit) <= tuple(numbers):
            raise ValueError("New version must be greater than the current version")
        return explicit
    index = {"major": 0, "minor": 1, "patch": 2}[part]
    numbers[index] += 1
    for position in range(index + 1, 3):
        numbers[position] = 0
    return ".".join(map(str, numbers))


def bump(part: str, explicit: str | None) -> None:
    old = check_versions()
    new = next_version(old, part, explicit)
    # Validate and prepare all edits before changing versioned files.
    paths = [
        ROOT / "VERSION", ROOT / "packages/node/package.json",
        ROOT / "packages/node/package-lock.json",
        ROOT / "packages/python/pyproject.toml", ROOT / "packages/java/pom.xml",
        ROOT / "README.md", ROOT / "packages/java/README.md",
        ROOT / "packages/shell/README.md", ROOT / "docs/releases.md",
    ]
    edits = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if path.name == "package-lock.json":
            lock = json.loads(text)
            lock["version"] = new
            lock["packages"][""]["version"] = new
            edits[path] = json.dumps(lock, indent=2) + "\n"
        elif path.name == "package.json":
            edits[path] = text.replace(f'"version": "{old}"', f'"version": "{new}"', 1)
        elif path.name == "pyproject.toml":
            edits[path] = text.replace(f'version = "{old}"', f'version = "{new}"', 1)
        elif path.name == "pom.xml":
            edits[path] = text.replace(f"<version>{old}</version>", f"<version>{new}</version>", 1)
        else:
            edits[path] = text.replace(old, new)
    for path, text in edits.items():
        path.write_text(text, encoding="utf-8")
    run(sys.executable, "scripts/package_shell.py")
    for suffix in ("tar.gz", "zip"):
        (ROOT / f"packages/shell/dist/curtail-str-shell-{old}.{suffix}").unlink(missing_ok=True)
    check_versions()
    print(f"Version updated: {old} -> {new}. Review and commit before tagging.")


def git(*args: str) -> str:
    return run("git", *args, capture=True)


def tags(version: str) -> tuple[str, str]:
    return f"v{version}", f"packages/go/v{version}"


def preflight(confirm: str, require_remote: bool = False) -> str:
    version = check_versions()
    if confirm != version:
        raise ValueError(f"Explicit confirmation required: CONFIRM={version}")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Release requires a clean Git tree, including untracked files")
    if git("branch", "--show-current") != "main":
        raise ValueError("Release requires the main branch")
    remote = git("remote", "get-url", "origin")
    if remote not in (REPOSITORY + ".git", REPOSITORY, "git@github.com:alansferreira/curtail-str.git"):
        raise ValueError("origin must point to alansferreira/curtail-str")
    head = git("rev-parse", "HEAD")
    for tag in tags(version):
        existing = git("tag", "--list", tag)
        if existing and git("rev-list", "-n", "1", tag) != head:
            raise ValueError(f"Tag {tag} already points to another commit")
    if require_remote:
        remote_main = git("ls-remote", "--exit-code", "origin", "refs/heads/main").split()[0]
        if remote_main != head:
            raise ValueError("Push the release commit to origin/main before publishing")
        for tag in tags(version):
            refs = git("ls-remote", "origin", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}")
            if refs:
                entries = dict(line.split()[::-1] for line in refs.splitlines())
                remote_head = entries.get(f"refs/tags/{tag}^{{}}", entries.get(f"refs/tags/{tag}"))
                if remote_head != head:
                    raise ValueError(f"Remote tag {tag} points to another commit")
    return version


def create_tags(version: str) -> None:
    for tag in tags(version):
        if not git("tag", "--list", tag):
            run("git", "tag", "-a", tag, "-m", f"curtail-str {version}")


def reuse_remote_tags(version: str) -> None:
    for tag in tags(version):
        if not git("tag", "--list", tag) and git("ls-remote", "origin", f"refs/tags/{tag}"):
            run("git", "fetch", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}")


def python_artifacts(version: str) -> tuple[Path, Path]:
    directory = ROOT / "packages/python/dist"
    return (
        directory / f"curtail_str-{version}-py3-none-any.whl",
        directory / f"curtail_str-{version}.tar.gz",
    )


def build(runtime: str) -> None:
    version = check_versions()
    if runtime == "node":
        directory = ROOT / "packages/node/dist"
        directory.mkdir(exist_ok=True)
        run("npm", "pack", "--pack-destination", str(directory), cwd=ROOT / "packages/node")
    elif runtime == "python":
        run(sys.executable, "-m", "build", "packages/python")
        artifacts = tuple(map(str, python_artifacts(version)))
        run(sys.executable, "-m", "twine", "check", "--strict", *artifacts)
        run(sys.executable, "scripts/check_python_distribution.py", *artifacts)
    elif runtime == "go":
        run("go", "build", "./...", cwd=ROOT / "packages/go")


def require_environment(*names: str) -> None:
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))


def publish(runtime: str, confirm: str, mvn: str) -> None:
    version = preflight(confirm, require_remote=True)
    selected = ("node", "python", "java", "go") if runtime == "all" else (runtime,)
    # Complete local credential/artifact checks before any remote mutation.
    if "node" in selected:
        if not (ROOT / f"packages/node/dist/curtail-str-{version}.tgz").is_file():
            raise ValueError("Build the npm tarball first")
        run("npm", "whoami", "--registry=https://registry.npmjs.org/")
    if "python" in selected:
        require_environment("TWINE_USERNAME", "TWINE_PASSWORD")
        artifacts = tuple(map(str, python_artifacts(version)))
        run(sys.executable, "-m", "twine", "check", "--strict", *artifacts)
    if "java" in selected:
        require_environment("CENTRAL_USERNAME", "CENTRAL_PASSWORD")
        if not shutil.which(mvn):
            raise ValueError(f"Maven executable not found: {mvn}")
        keys = run("gpg", "--list-secret-keys", "--with-colons", capture=True)
        if not any(line.startswith("sec:") for line in keys.splitlines()):
            raise ValueError("A GPG secret key is required for Maven Central signing")
    reuse_remote_tags(version)
    create_tags(version)
    run("git", "push", "--atomic", "origin", *(f"refs/tags/{tag}" for tag in tags(version)))
    if "go" in selected:
        print(f"Go version published by tag: packages/go/v{version}")
    if "node" in selected:
        run("npm", "publish", str(ROOT / f"packages/node/dist/curtail-str-{version}.tgz"),
            "--access=public", "--registry=https://registry.npmjs.org/")
    if "python" in selected:
        run(sys.executable, "-m", "twine", "upload", "--non-interactive",
            "--repository-url", "https://upload.pypi.org/legacy/",
            *map(str, python_artifacts(version)))
    if "java" in selected:
        run(mvn, "-B", "-ntp", "-s", "scripts/maven-settings.xml",
            "-f", "packages/java/pom.xml", "-Prelease", "clean", "deploy")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version")
    commands.add_parser("check")
    bump_parser = commands.add_parser("bump")
    bump_parser.add_argument("--part", choices=("patch", "minor", "major"), default="patch")
    bump_parser.add_argument("--version")
    for name in ("preflight", "tag", "publish"):
        command = commands.add_parser(name)
        command.add_argument("--confirm", default="")
        if name == "publish":
            command.add_argument("runtime", choices=("all", "node", "python", "go", "java"))
            command.add_argument("--mvn", default="mvn")
    build_parser = commands.add_parser("build")
    build_parser.add_argument("runtime", choices=("node", "python", "go"))
    args = parser.parse_args()
    try:
        if args.command == "version":
            print(current_version())
        elif args.command == "check":
            print(f"Shared version: {check_versions()}")
        elif args.command == "bump":
            bump(args.part, args.version)
        elif args.command == "build":
            build(args.runtime)
        elif args.command == "preflight":
            print(f"Release preflight passed: {preflight(args.confirm)}")
        elif args.command == "tag":
            create_tags(preflight(args.confirm))
        elif args.command == "publish":
            publish(args.runtime, args.confirm, args.mvn)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Release failed: {error}\n")


if __name__ == "__main__":
    main()
