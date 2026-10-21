import copy
import json
from pathlib import Path
import unittest

from abbrev import abbrev


class ContractTest(unittest.TestCase):
    def test_shared_cases(self):
        path = Path(__file__).resolve().parents[3] / "spec" / "cases.json"
        names = {
            "minWordLength": "min_word_length",
            "preserveWordLength": "preserve_word_length",
            "maxWordLength": "max_word_length",
        }
        for item in json.loads(path.read_text(encoding="utf-8")):
            with self.subTest(name=item["name"]):
                options = {names.get(k, k): v for k, v in item.get("options", {}).items()}
                snapshot = copy.deepcopy(options)
                if item.get("error"):
                    with self.assertRaises((TypeError, ValueError)):
                        abbrev(item["input"], options)
                else:
                    self.assertEqual(
                        abbrev(item["input"], options), item["expected"]
                    )
                    self.assertEqual(
                        abbrev(item["input"], options), item["expected"]
                    )
                self.assertEqual(options, snapshot)

    def test_dynamic_errors(self):
        for value in [1, [], {}, True, "\ud800"]:
            with self.subTest(value=repr(value)), self.assertRaises(TypeError):
                abbrev(value)
        for options in [
            [], {"unknown": 1}, {"mode": None},
            {"mode": "configurable", "max_word_length": True},
            {"mode": "configurable", "max_word_length": 1.5},
            {"mode": "custom", "replacements": None},
            {"mode": "custom", "replacements": {"abc": 1}},
            {"mode": "custom", "replacements": {"abc": "\ud800"}},
        ]:
            with self.subTest(options=repr(options)), self.assertRaises((TypeError, ValueError)):
                abbrev("", options)


if __name__ == "__main__":
    unittest.main()
