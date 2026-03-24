import os
import sys
import logging
from time import sleep
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing in .env file")

# Logging setup
logging.basicConfig(level=logging.INFO)

# ---------- Backend Functions ----------

def read_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")
    if os.path.getsize(file_path) == 0:
        raise ValueError("File is empty")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def truncate_code(code, max_chars=8000):
    return code[:max_chars] if len(code) > max_chars else code

def load_prompt():
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

def invoke_with_retry(client, messages, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return client.invoke(messages)
        except Exception as e:
            log(f"Retry {attempt+1} failed: {e}")
            sleep(delay)
    raise Exception("All retries failed")

def save_output(content):
    with open("review.txt", "w", encoding="utf-8") as f:
        f.write(content)

# ---------- UI Functions ----------

def log(message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)

def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

        try:
            code = read_file(file_path)
            code_preview.delete("1.0", tk.END)
            code_preview.insert(tk.END, code)
            log("File loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def run_review():
    file_path = file_entry.get()

    if not file_path:
        messagebox.showwarning("Warning", "Please select a file first.")
        return

    try:
        log("Reading file...")
        code = read_file(file_path)
        code = truncate_code(code)

        log("Loading prompt...")
        prompt_template = load_prompt()
        final_prompt = prompt_template.replace("{code}", code)

        log("Initializing AI...")
        client = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

        messages = [
            {"role": "system", "content": "You are a strict senior software engineer who reviews code clearly."},
            {"role": "user", "content": final_prompt}
        ]

        log("Sending request...")
        response = invoke_with_retry(client, messages)

        review_box.delete("1.0", tk.END)
        review_box.insert(tk.END, response.content)

        save_output(response.content)
        log("Review completed and saved!")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        log(f"Error: {e}")

# ---------- UI Layout ----------

root = tk.Tk()
root.title("AI Code Reviewer")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")

# Top Frame (File selection)
top_frame = ttk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=10)

file_entry = ttk.Entry(top_frame, width=80)
file_entry.pack(side="left", padx=5)

browse_btn = ttk.Button(top_frame, text="Browse", command=browse_file)
browse_btn.pack(side="left", padx=5)

run_btn = ttk.Button(top_frame, text="Run Review", command=run_review)
run_btn.pack(side="left", padx=5)

# Middle Frame (Code + Review)
middle_frame = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Code Preview
code_frame = ttk.LabelFrame(middle_frame, text="Code")
code_preview = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, height=20)
code_preview.pack(fill="both", expand=True)
middle_frame.add(code_frame, weight=1)

# Review Output
review_frame = ttk.LabelFrame(middle_frame, text="AI Review")
review_box = scrolledtext.ScrolledText(review_frame, wrap=tk.WORD, height=20)
review_box.pack(fill="both", expand=True)
middle_frame.add(review_frame, weight=1)

# Bottom Frame (Logs)
bottom_frame = ttk.LabelFrame(root, text="Logs")
bottom_frame.pack(fill="both", padx=10, pady=5)

log_box = scrolledtext.ScrolledText(bottom_frame, height=8, bg="black", fg="lime")
log_box.pack(fill="both", expand=True)

root.mainloop()