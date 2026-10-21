import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/shell"


class ShellTest(unittest.TestCase):
    def check_command(self, command, text, expected):
        result = subprocess.run(command + [text], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.rstrip("\r\n"), expected)
        self.assertEqual(result.stderr, "")

    @unittest.skipUnless(os.name != "nt" and shutil.which("awk"), "Requires POSIX shell and awk")
    def test_posix_contract(self):
        for case in json.loads((ROOT / "spec/cases.json").read_text(encoding="utf-8")):
            if case.get("options") or case.get("error"):
                continue
            text = case["input"]
            if text is None or not text.isascii():
                continue
            with self.subTest(name=case["name"]):
                self.check_command(["sh", str(PACKAGE / "curtail-str.sh")], text, case["expected"])
        for text, expected in [
            ("", ""), ("CODE_IN_THE_STOCK", "cd-the-stck"),
            ("abc\ncodigo", "abc-cdg"), ("abc\\ndef", "abc\\"),
            ("a!!b", "a!!b"), ("$HOME xyz", "$hm-xyz"),
        ]:
            with self.subTest(text=text):
                self.check_command(["sh", str(PACKAGE / "curtail-str.sh")], text, expected)

    @unittest.skipUnless(os.name != "nt" and shutil.which("awk"), "Requires POSIX shell and awk")
    def test_posix_arguments(self):
        command = ["sh", str(PACKAGE / "curtail-str.sh")]
        for arguments in ([], ["one", "two"]):
            result = subprocess.run(command + arguments, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertTrue(result.stderr)
        self.check_command(command, "--help", "Usage: sh curtail-str.sh \"text\"\n"
                           "Universal mode. Requires POSIX awk; Unicode behavior depends on awk and locale.")

    @unittest.skipUnless(os.name == "nt", "Requires native Windows CMD")
    def test_batch(self):
        for text, expected in [
            ("codigo-do-cliente-ativo-no-estoque", "cdg-clnt-atv-estq"),
            ("active-customer-code-in-the-stock", "actv-cstm-cd-the-stck"),
            ("SKU_API-sys", "sku-api-sys"), ("", ""), ("a de do", ""),
            ("batata assassino", "bt-asn"), ("a1122", "a112"),
        ]:
            with self.subTest(text=text):
                command = f'call "{PACKAGE / "curtail-str.bat"}" "{text}"'
                result = subprocess.run(["cmd.exe", "/d", "/c", command],
                                        capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.rstrip("\r\n"), expected)

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"),
                         "Requires PowerShell")
    def test_powershell(self):
        executable = shutil.which("pwsh") or shutil.which("powershell")
        for text, expected in [
            ("codigo-do-cliente-ativo-no-estoque", "cdg-clnt-atv-estq"),
            ("active-customer-code-in-the-stock", "actv-cstm-cd-the-stck"),
            ("", ""), ("batata assassino", "bt-asn"),
            ("coração", "crç"), ("Árvore", "árvr"),
        ]:
            with self.subTest(text=text):
                self.check_command(
                    [executable, "-NoProfile", "-File", str(PACKAGE / "curtail-str.ps1"), "-Text"],
                    text, expected,
                )


if __name__ == "__main__":
    unittest.main()
