import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import sys
import logging
from time import sleep

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing in .env file")

def read_file(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError
        
        if os.path.getsize(file_path) == 0:
            raise ValueError("File is empty")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        
    except FileNotFoundError:
        logging.error("File not found. Please check the path.")
        sys.exit()
        
    except PermissionError:
        logging.error("Permission denied while opening the file.")
        sys.exit()
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit()

def load_prompt():
    try:
        return read_file("prompt.txt")
    except Exception:
        logging.error("Error loading prompt.txt")
        sys.exit()

def truncate_code(code, max_chars=8000):
    if len(code) > max_chars:
        logging.warning("Code too large, truncating...")
        return code[:max_chars]
    return code

def invoke_with_retry(client, messages, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return client.invoke(messages)
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
            sleep(delay)

        logging.error("All retry attempts failed.")
        sys.exit()

def save_output(content):
    try:
        with open("review.txt", "w", encoding="utf-8") as f:
            f.write(content)
            logging.info("Review saved to review.txt")
    except Exception as e:
        logging.error(f"Failed to save output: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <code_file>")
        sys.exit()
    
    file_path = sys.argv[1]

    logging.info("Reading code file...")
    code = read_file(file_path)

    code = truncate_code(code)

    logging.info("Loading prompt template...")
    prompt_template = load_prompt()

    final_prompt = prompt_template.replace("{code}", code)

    logging.info("Intializing AI client...")
    client = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.2
    )

    messages = [
        {"role": "system", "content": "You are a strict senior software engineer who reviews code clearly."},
        {"role": "user", "content": final_prompt}
    ]

    logging.info("Sending code for review...")
    response = invoke_with_retry(client, messages)

    print("\n====== AI CODE REVIEW ======\n")
    print(response.content)
    print("\n==============\n")

    save_output(response.content)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
