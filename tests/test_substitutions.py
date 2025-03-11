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
                "substitutions": {"foo": "bar", "baz": "qux"},
                "input_text": "127.0.0.1",
                "expected_output": "127.0.0.1"
            },
            {
                "substitutions": {"foo": "bar", "baz": "qux"},
                "input_text": "0.0.0.0",
                "expected_output": "0.0.0.0"
            },
         ]
    
    def strings_provider(self):
        return [
            '11.23.44.55',  
            'password: 678fsf7d6sf'         
         ]
    
    def test_text_transformation(self):
        for case in self.data_provider():
            obfuscated_text = replace_text(case["input_text"], case["substitutions"], obfuscate=True)
            self.assertEqual(obfuscated_text, case["expected_output"])
            
            deobfuscated_text = replace_text(obfuscated_text, {v: k for k, v in case["substitutions"].items()}, obfuscate=False)
            self.assertEqual(deobfuscated_text, case["input_text"])

    def test_text_obfuscated(self):
        for text in self.strings_provider():
            obfuscated_text = replace_text(text, {}, obfuscate=True)
            self.assertNotEqual(obfuscated_text, text)
            self.assertEqual(text, replace_text(obfuscated_text, {}, obfuscate=False))
            

if __name__ == "__main__":
    unittest.main()
