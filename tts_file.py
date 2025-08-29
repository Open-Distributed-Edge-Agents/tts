import sys
import requests
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    url = os.getenv("TTS_FUNCTION_URL")
    if not url:
        print("TTS_FUNCTION_URL not found in environment. Please set it in .env file.")
        sys.exit(1)

    token = os.getenv("TOKEN")
    if not token:
        print("TOKEN not found in environment. Please set it in .env file.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python tts_file.py text_file_to_convert.txt")
        sys.exit(1)

    file_name = sys.argv[1]
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    payload = {
        "token": token,
        "text": text
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        with open("output.ogg", "wb") as f:
            f.write(response.content)

        print("OGG file saved as output.ogg")
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()
