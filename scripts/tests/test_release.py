import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("release", ROOT / "scripts/release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseTest(unittest.TestCase):
    def test_semver_bumps(self):
        for part, expected in (("patch", "1.2.4"), ("minor", "1.3.0"), ("major", "2.0.0")):
            self.assertEqual(release.next_version("1.2.3", part), expected)
        self.assertEqual(release.next_version("0.1.1", "patch", "1.0.0"), "1.0.0")

    def test_reject_invalid_versions(self):
        for value in ("1.2", "v1.2.3", "01.2.3", "1.2.3-rc.1", "1.2.3+build", "1.2.3\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                release.parse_version(value)
        for value in ("1.2.3", "1.0.0"):
            with self.assertRaises(ValueError):
                release.next_version("1.2.3", "patch", value)

    def test_shared_metadata(self):
        self.assertEqual(release.check_versions(), (ROOT / "VERSION").read_text().strip())

    def test_bump_real_fixture(self):
        with tempfile.TemporaryDirectory(prefix="curtail-release-test-") as directory:
            target = Path(directory)
            paths = [
                "VERSION", "LICENSE", "Makefile", "README.md", "docs/releases.md", "packages/node/package.json",
                "packages/node/package-lock.json", "packages/python/pyproject.toml",
                "packages/java/pom.xml", "packages/java/README.md",
                "packages/shell/README.md", "packages/shell/curtail-str.sh",
                "packages/shell/curtail-str.bat", "packages/shell/curtail-str.ps1",
                "scripts/package_shell.py", "scripts/release.py",
                *(f"packages/{name}/LICENSE" for name in ("node", "python", "go", "java")),
            ]
            for name in paths:
                (target / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target / name)
            with patch.object(release, "ROOT", target):
                current = release.check_versions()
                expected = release.next_version(current, "patch")
                subprocess.run(
                    ["make", "bump", "PART=patch", f"PYTHON={sys.executable}"],
                    cwd=target, check=True,
                )
                self.assertEqual(release.check_versions(), expected)
                lock = json.loads((target / "packages/node/package-lock.json").read_text())
                self.assertEqual(lock["packages"][""]["version"], expected)
                self.assertTrue((target / f"packages/shell/dist/curtail-str-shell-{expected}.zip").is_file())
                self.assertNotIn(current, (target / "packages/shell/README.md").read_text())
                before = (target / "VERSION").read_bytes()
                with self.assertRaises(ValueError):
                    release.bump("patch", current)
                self.assertEqual((target / "VERSION").read_bytes(), before)

    def fake_git(self, *args):
        responses = {
            ("status", "--porcelain", "--untracked-files=all"): "",
            ("branch", "--show-current"): "main",
            ("remote", "get-url", "origin"): release.REPOSITORY + ".git",
            ("rev-parse", "HEAD"): "abc123",
            ("ls-remote", "--exit-code", "origin", "refs/heads/main"):
                "abc123\trefs/heads/main",
        }
        if args[0] in ("tag", "ls-remote"):
            return responses.get(args, "")
        return responses[args]

    def test_confirmation_required_before_any_git_call(self):
        with patch.object(release, "git") as git:
            with self.assertRaisesRegex(ValueError, "confirmation"):
                release.preflight("")
            git.assert_not_called()

    def test_dirty_tree_rejected(self):
        with patch.object(release, "git", return_value=" M VERSION"):
            with self.assertRaisesRegex(ValueError, "clean"):
                release.preflight(release.current_version())

    def test_wrong_branch_and_remote_rejected(self):
        for selector, value in (
            (("branch", "--show-current"), "feature"),
            (("remote", "get-url", "origin"), "https://example.com/wrong.git"),
        ):
            with self.subTest(selector=selector):
                def git(*args):
                    return value if args == selector else self.fake_git(*args)
                with patch.object(release, "git", side_effect=git):
                    with self.assertRaises(ValueError):
                        release.preflight(release.current_version())

    def test_unpushed_commit_rejected(self):
        def git(*args):
            if args[:2] == ("ls-remote", "--exit-code"):
                return "different\trefs/heads/main"
            return self.fake_git(*args)
        with patch.object(release, "git", side_effect=git):
            with self.assertRaisesRegex(ValueError, "Push"):
                release.preflight(release.current_version(), require_remote=True)

    def test_conflicting_local_tag_rejected(self):
        def git(*args):
            if args[0] == "tag":
                return args[-1]
            if args[0] == "rev-list":
                return "different"
            return self.fake_git(*args)
        with patch.object(release, "git", side_effect=git):
            with self.assertRaisesRegex(ValueError, "another commit"):
                release.preflight(release.current_version())

    def test_conflicting_remote_tag_rejected(self):
        def git(*args):
            if args[:2] == ("ls-remote", "origin"):
                return f"different\t{args[-2]}\nother\t{args[-1]}"
            return self.fake_git(*args)
        with patch.object(release, "git", side_effect=git):
            with self.assertRaisesRegex(ValueError, "Remote tag"):
                release.preflight(release.current_version(), require_remote=True)

    def test_go_publish_uses_subdirectory_tag(self):
        with patch.object(release, "git", side_effect=self.fake_git), \
                patch.object(release, "run") as run:
            version = release.current_version()
            release.publish("go", version, "mvn")
            run.assert_any_call(
                "git", "push", "--atomic", "origin",
                f"refs/tags/v{version}", f"refs/tags/packages/go/v{version}",
            )
            self.assertFalse(any(call.args[0] in ("npm", "mvn") for call in run.call_args_list))

    def test_retry_reuses_remote_annotated_tags(self):
        version = release.current_version()

        def git(*args):
            if args[:2] == ("tag", "--list"):
                return ""
            if args[:2] == ("ls-remote", "origin"):
                return f"tag-object\t{args[-1]}"
            return self.fake_git(*args)

        with patch.object(release, "git", side_effect=git), patch.object(release, "run") as run:
            release.reuse_remote_tags(version)
            for tag in release.tags(version):
                run.assert_any_call(
                    "git", "fetch", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}",
                )

    def test_missing_credentials_do_not_create_tags(self):
        with patch.object(release, "git", side_effect=self.fake_git), \
                patch.dict(os.environ, {}, clear=True), \
                patch.object(release, "create_tags") as tags:
            with self.assertRaisesRegex(ValueError, "TWINE"):
                release.publish("python", release.current_version(), "mvn")
            tags.assert_not_called()

    def test_registry_upload_commands(self):
        version = release.current_version()
        environment = {
            "TWINE_USERNAME": "__token__", "TWINE_PASSWORD": "test-only",
            "CENTRAL_USERNAME": "test-only", "CENTRAL_PASSWORD": "test-only",
        }

        def run(*args, **kwargs):
            return "sec:test-key" if args[:2] == ("gpg", "--list-secret-keys") else ""

        with patch.object(release, "preflight", return_value=version), \
                patch.object(release, "create_tags"), \
                patch.object(release, "run", side_effect=run) as command, \
                patch.object(release.shutil, "which", return_value="/tools/mvn"), \
                patch.object(Path, "is_file", return_value=True), \
                patch.dict(os.environ, environment, clear=True):
            release.publish("all", version, "/tools/mvn")
            command.assert_any_call(
                "npm", "publish", str(ROOT / f"packages/node/dist/curtail-str-{version}.tgz"),
                "--access=public", "--registry=https://registry.npmjs.org/",
            )
            command.assert_any_call(
                sys.executable, "-m", "twine", "upload", "--non-interactive",
                "--repository-url", "https://upload.pypi.org/legacy/",
                *map(str, release.python_artifacts(version)),
            )
            command.assert_any_call(
                "/tools/mvn", "-B", "-ntp", "-s", "scripts/maven-settings.xml",
                "-f", "packages/java/pom.xml", "-Prelease", "clean", "deploy",
            )

    def test_missing_signing_key_does_not_push(self):
        with patch.object(release, "preflight", return_value=release.current_version()), \
                patch.object(release.shutil, "which", return_value="/tools/mvn"), \
                patch.object(release, "run", return_value="") as command, \
                patch.object(release, "create_tags") as tags, \
                patch.dict(os.environ, {"CENTRAL_USERNAME": "test", "CENTRAL_PASSWORD": "test"}):
            with self.assertRaisesRegex(ValueError, "GPG secret key"):
                release.publish("java", release.current_version(), "mvn")
            tags.assert_not_called()
            self.assertFalse(any(call.args[:2] == ("git", "push") for call in command.call_args_list))

    def test_make_publish_is_guarded(self):
        result = subprocess.run(
            ["make", "release-check", f"PYTHON={sys.executable}", "CONFIRM="],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("confirmation", result.stderr)


if __name__ == "__main__":
    unittest.main()
