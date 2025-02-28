import unittest
import sys
import os
import tkinter
tkinter.Tk = lambda: None  # Prevents Tkinter windows from opening
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from obfuscator import replace_text, SUBSTITUTIONS, REVERSE_SUBSTITUTIONS


class TestObfuscator(unittest.TestCase):
    
    def data_provider(self):
        return [
            {
                "substitutions": {"hello": "hi", "world": "earth"},
                "input_text": "hello world!",
                "expected_output": "hi earth!"
            },
            {
                "substitutions": {"foo": "bar", "baz": "qux"},
                "input_text": "foo and baz",
                "expected_output": "bar and qux"
            },
            {
                "substitutions": {"password": "secret123"},
                "input_text": "My password: hunter2",
                "expected_output": "My password: secret123"
            },
        ]
    
    def test_text_transformation(self):
        for case in self.data_provider():
            obfuscated_text = replace_text(case["input_text"], case["substitutions"], obfuscate=True)
            self.assertEqual(obfuscated_text, case["expected_output"])
            
            deobfuscated_text = replace_text(obfuscated_text, {v: k for k, v in case["substitutions"].items()}, obfuscate=False)
            self.assertEqual(deobfuscated_text, case["input_text"])

if __name__ == "__main__":
    unittest.main()
