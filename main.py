import json
from pathlib import Path
from datetime import datetime

import ollama


MODEL_NAME = "qwen2.5:7b"

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompts" / "virtual_hacker_prompt.txt"
TARGET_PATH = BASE_DIR / "examples" / "target_chatbot.json"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "risk_report.md"


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def load_json_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_user_message(target_system: dict) -> str:
    target_json = json.dumps(target_system, indent=2, ensure_ascii=False)

    return f"""
Analyze the following LLM-based chatbot system.

Target system description:

```json
{target_json}