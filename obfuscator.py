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

def replace_text(event=None):
    """Replace predefined words in the text box with substitutions, case-insensitive."""
    if getattr(replace_text, "in_progress", False):  # Prevent recursive updates
        return
    
    # Check if Ctrl+A is pressed and skip replacement
    if event and event.state & 0x4 and event.keysym == "a":  # Ctrl+A
        return
    
    replace_text.in_progress = True  # Set flag to indicate ongoing replacement
    try:
        input_text = text_box.get("1.0", tk.END)
        if not SUBSTITUTIONS:
            return  # No substitutions loaded
        
        cursor_position = text_box.index(tk.INSERT)  # Save current cursor position
        cursor_line, cursor_col = map(int, cursor_position.split('.'))
        
        def replacement_function(match):
            original_word = match.group()
            replacement_word = SUBSTITUTIONS[original_word.lower()]
            return match_case(replacement_word, original_word)
        
        # Create a regex pattern for all substitution words (case insensitive)
        pattern = re.compile('|'.join(map(re.escape, SUBSTITUTIONS.keys())), re.IGNORECASE)
        modified_text = pattern.sub(replacement_function, input_text)
        
        # Update the text box content
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, modified_text)
        
        # Adjust cursor position
        new_position_index = calculate_new_cursor_position(input_text, modified_text, cursor_line, cursor_col)
        text_box.mark_set(tk.INSERT, new_position_index)
    finally:
        replace_text.in_progress = False  # Reset flag

def calculate_new_cursor_position(original_text, modified_text, line, col):
    """Calculate new cursor position after text modifications."""
    original_lines = original_text.splitlines()
    modified_lines = modified_text.splitlines()
    
    # Adjust for current line
    if line <= len(original_lines) and line <= len(modified_lines):
        original_line_text = original_lines[line - 1][:col]
        modified_line_text = modified_lines[line - 1]
        
        # Map the cursor's column to the new text
        prefix = modified_line_text[:len(original_line_text)]
        col = len(prefix)  # Update column to match the new length
    
    # Return updated cursor position
    return f"{line}.{col}"

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

# Bind the replace_text function to text input events
text_box.bind("<KeyRelease>", replace_text)  # Trigger on key release
text_box.bind("<Control-v>", replace_text)  # Trigger on paste (Ctrl+V)
text_box.bind("<Control-a>", lambda event: "break")  # Prevent immediate modification on Ctrl+A

# Create the "Copy" button
copy_button = tk.Button(root, text="Copy", command=copy_to_clipboard)
copy_button.pack(pady=5)

# Run the application
root.mainloop()
