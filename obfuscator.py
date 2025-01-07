import tkinter as tk
from tkinter import messagebox
import re
import os

# Dynamically determine the path to the substitutions file
script_dir = os.path.dirname(os.path.abspath(__file__))
SUBSTITUTIONS_FILE = os.path.join(script_dir, "substitutions.txt")

def load_substitutions(file_path):
    """Load substitutions from a file into a dictionary."""
    substitutions = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip() and "," in line:
                    original, replacement = map(str.strip, line.split(",", 1))
                    substitutions[original.lower()] = replacement
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_path}' not found.")
    return substitutions

def match_case(replacement, original):
    """Adjust the replacement word to match the case of the original word."""
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()

def replace_text():
    """Replace predefined words in the text box with substitutions, case-insensitive."""
    input_text = text_box.get("1.0", tk.END)
    if not SUBSTITUTIONS:
        messagebox.showerror("Error", "No substitutions loaded.")
        return
    
    def replacement_function(match):
        original_word = match.group()
        replacement_word = SUBSTITUTIONS[original_word.lower()]
        return match_case(replacement_word, original_word)
    
    # Create a regex pattern for all substitution words (case insensitive)
    pattern = re.compile('|'.join(map(re.escape, SUBSTITUTIONS.keys())), re.IGNORECASE)
    modified_text = pattern.sub(replacement_function, input_text, 0)
    
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, modified_text)

def copy_to_clipboard():
    """Copy the modified text to the clipboard."""
    modified_text = text_box.get("1.0", tk.END).strip()
    if not modified_text:
        messagebox.showinfo("Info", "Nothing to copy to clipboard!")
        return
    root.clipboard_clear()
    root.clipboard_append(modified_text)
    root.update()  # Required to update the clipboard
    messagebox.showinfo("Info", "Text copied to clipboard!")

# Load substitutions from the file
SUBSTITUTIONS = load_substitutions(SUBSTITUTIONS_FILE)

# Create the main application window
root = tk.Tk()
root.title("Text Substitution Tool")

# Create a text box
text_box = tk.Text(root, wrap="word", height=10, width=50)
text_box.pack(padx=10, pady=10)

# Create the "Go" button
go_button = tk.Button(root, text="Go", command=replace_text)
go_button.pack(pady=5)

# Create the "Copy" button
copy_button = tk.Button(root, text="Copy", command=copy_to_clipboard)
copy_button.pack(pady=5)

# Run the application
root.mainloop()
