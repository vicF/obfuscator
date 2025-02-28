import tkinter as tk
from tkinter import messagebox
import re
import os
import ipaddress

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

SUBSTITUTIONS = load_substitutions(SUBSTITUTIONS_FILE)
REVERSE_SUBSTITUTIONS = {v.lower(): k for k, v in SUBSTITUTIONS.items()}

def match_case(replacement, original):
    """Adjust the replacement word to match the case of the original word."""
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()

def obfuscate_ip(ip):
    """Obfuscate an IP address while keeping it valid."""
    try:
        parsed_ip = ipaddress.ip_address(ip)
        if parsed_ip.is_private or ip in {"127.0.0.1", "0.0.0.0"}:
            return ip  # Keep special/private IPs unchanged
        octets = ip.split(".")
        obfuscated_octets = [str((int(o) + 100) % 255) for o in octets]  # Shift octets
        return ".".join(obfuscated_octets)
    except ValueError:
        return ip

def deobfuscate_ip(ip):
    """Reverse obfuscation of an IP address."""
    try:
        octets = ip.split(".")
        deobfuscated_octets = [str((int(o) - 100) % 255) for o in octets]
        return ".".join(deobfuscated_octets)
    except ValueError:
        return ip

def obfuscate_password(password):
    """Simple reversible obfuscation for passwords."""
    return password[::-1]  # Reverse the password for obfuscation

def deobfuscate_password(password):
    """Reverse obfuscation for passwords."""
    return password[::-1]  # Reverse it back

def replace_text(input_text, mapping, obfuscate=True):
    """Replace words in the input text using the given mapping and obfuscate IPs and passwords."""
    def replacement_function(match):
        original_word = match.group()
        if original_word in mapping:
            return match_case(mapping[original_word.lower()], original_word)
        elif re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', original_word):
            return obfuscate_ip(original_word) if obfuscate else deobfuscate_ip(original_word)
        elif re.match(r'(PASSWORD:|\$password=|\$pass=)["\']?([^"\']+)["\']?', original_word, re.IGNORECASE):
            return re.sub(r'(["\']?)([^"\']+)(["\']?)$', lambda m: m.group(1) + (obfuscate_password(m.group(2)) if obfuscate else deobfuscate_password(m.group(2))) + m.group(3), original_word)
        return original_word
    
    pattern = re.compile('|'.join(map(re.escape, mapping.keys())) + r'|\b(?:\d{1,3}\.){3}\d{1,3}\b|(?:PASSWORD:|\$password=|\$pass=)["\']?([^"\']+)["\']?', re.IGNORECASE)
    return pattern.sub(replacement_function, input_text)

def update_text(event, source, target, mapping, obfuscate):
    """Update the target text box based on input in the source text box."""
    input_text = source.get("1.0", tk.END).strip()
    if input_text:
        modified_text = replace_text(input_text, mapping, obfuscate)
        target.delete("1.0", tk.END)
        target.insert(tk.END, modified_text)
        copy_to_clipboard(modified_text)
        show_status("Text copied to clipboard")

def copy_to_clipboard(text):
    """Copy text to clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

def show_status(message):
    """Show a temporary status message."""
    status_label.config(text=message)
    root.after(2000, lambda: status_label.config(text=""))  # Clear message after 2 seconds

def clear_text():
    """Clear both text areas."""
    left_text.delete("1.0", tk.END)
    right_text.delete("1.0", tk.END)
    show_status("Text cleared")

# Create the main application window
root = tk.Tk()
root.title("Bidirectional Text Substitution Tool")

# Create a frame to hold both text boxes
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create the left text box
left_text = tk.Text(frame, wrap="word", height=10, width=40)
left_text.pack(side=tk.LEFT, padx=5)
left_text.bind("<KeyRelease>", lambda event: update_text(event, left_text, right_text, SUBSTITUTIONS, True))
left_text.bind("<Control-v>", lambda event: update_text(event, left_text, right_text, SUBSTITUTIONS, True))

# Create the right text box
right_text = tk.Text(frame, wrap="word", height=10, width=40)
right_text.pack(side=tk.RIGHT, padx=5)
right_text.bind("<KeyRelease>", lambda event: update_text(event, right_text, left_text, REVERSE_SUBSTITUTIONS, False))
right_text.bind("<Control-v>", lambda event: update_text(event, right_text, left_text, REVERSE_SUBSTITUTIONS, False))

# Create a status label
status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

# Create a Clear button
clear_button = tk.Button(root, text="Clear", command=clear_text)
clear_button.pack(pady=5)

# Run the application
root.mainloop()
