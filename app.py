import os
import sys
import logging
from time import sleep
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq

load_dotenv()

logging.basicConfig(level=logging.INFO)

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

    except Exception as e:
        logging.error(f"File error: {e}")
        sys.exit()


def load_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Prompt load error: {e}")
        sys.exit()


def truncate_code(code, max_chars=8000):
    return code[:max_chars]


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
    with open("review.txt", "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <code_file>")
        sys.exit()

    file_path = sys.argv[1]

    logging.info("Reading file...")
    code = read_file(file_path)
    code = truncate_code(code)

    logging.info("Loading prompt...")
    prompt_template = load_prompt()

    # ✅ SAFE PROMPT BUILDING (NO replace)
    final_prompt = f"""{prompt_template}

CODE:
```python
{code}
```"""

    logging.info("Initializing AI...")
    client = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0
    )

    messages = [
        {
            "role": "system",
            "content": "You are a strict code reviewer. Follow rules exactly. Do not hallucinate."
        },
        {
            "role": "user",
            "content": final_prompt
        }
    ]

    logging.info("Sending request...")
    response = invoke_with_retry(client, messages)

    print("\n====== AI CODE REVIEW ======\n")
    print(response.content)
    print("\n===========================\n")

    save_output(response.content)


if __name__ == "__main__":
    main()