import argparse
import json
from pathlib import Path
from datetime import datetime
from threading import Event
import time
import subprocess
from typing import Optional

import ollama
from jsonschema import validate, ValidationError


BASE_DIR = Path(__file__).resolve().parent

JSON_BUILDER_PROMPT_PATH = BASE_DIR / "prompts" / "json_builder_prompt.txt"
VIRTUAL_HACKER_PROMPT_PATH = BASE_DIR / "prompts" / "virtual_hacker_prompt.txt"

OUTPUT_DIR = BASE_DIR / "outputs"


TARGET_SYSTEM_SCHEMA = {
    "type": "object",
    "required": [
        "system_name",
        "system_type",
        "description",
        "reference_architecture",
        "users",
        "components",
        "data_handled",
        "security_assumptions",
        "attacker_model",
        "analysis_scope",
    ],
    "properties": {
        "system_name": {
            "type": "string",
            "minLength": 1,
        },
        "system_type": {
            "type": "string",
            "minLength": 1,
        },
        "description": {
            "type": "string",
            "minLength": 1,
        },
        "reference_architecture": {
            "type": "string",
            "minLength": 1,
        },
        "users": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "components": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "data_handled": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "security_assumptions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "attacker_model": {
            "type": "object",
            "required": [
                "attacker_type",
                "access_level",
                "capabilities",
                "limitations",
            ],
            "properties": {
                "attacker_type": {
                    "type": "string",
                    "minLength": 1,
                },
                "access_level": {
                    "type": "string",
                    "minLength": 1,
                },
                "capabilities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "limitations": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
            "additionalProperties": False,
        },
        "analysis_scope": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "prompt injection",
                    "privacy leakage",
                    "hallucination",
                    "resource exhaustion",
                    "tool misuse",
                    "unauthorized access",
                    "information disclosure",
                ],
            },
        },
    },
    "additionalProperties": False,
}


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def safe_filename(text: str) -> str:
    return text.replace(":", "_").replace("/", "_").replace("\\", "_").replace(" ", "_")


def validate_target_json(target_system: dict) -> None:
    try:
        validate(instance=target_system, schema=TARGET_SYSTEM_SCHEMA)
    except ValidationError as e:
        error_path = " -> ".join(str(part) for part in e.path)

        if error_path:
            location = f" at '{error_path}'"
        else:
            location = ""

        raise ValueError(
            f"Generated JSON does not match the required schema{location}.\n"
            f"Validation error: {e.message}"
        ) from e


def extract_json_from_model_output(raw_output: str) -> dict:
    cleaned_output = raw_output.strip()

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output.removeprefix("```json").strip()

    if cleaned_output.startswith("```"):
        cleaned_output = cleaned_output.removeprefix("```").strip()

    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output.removesuffix("```").strip()

    try:
        parsed_json = json.loads(cleaned_output)
    except json.JSONDecodeError as e:
        raise ValueError(
            "The model did not return valid JSON.\n"
            f"JSON parsing error: {e.msg} at line {e.lineno}, column {e.colno}\n\n"
            f"Raw model output:\n{raw_output}"
        ) from e

    if not isinstance(parsed_json, dict):
        raise ValueError(
            "The model returned valid JSON, but the top-level value is not an object."
        )

    return parsed_json


def _kill_ollama_on_stop(stop_event: Event):
    """Monitor stop_event and kill Ollama process when triggered."""
    stop_event.wait()
    
    if stop_event.is_set():
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/IM", "ollama.exe"],
                capture_output=True,
                timeout=2,
            )
        except Exception:
            try:
                subprocess.run(
                    ["pkill", "-f", "ollama"],
                    capture_output=True,
                    timeout=2,
                )
            except Exception:
                pass


def _raise_if_cancelled(stop_event: Optional[Event]) -> None:
    if stop_event is not None and stop_event.is_set():
        raise RuntimeError("Analysis stopped by user.")


def call_ollama(
    model_name: str,
    system_prompt: str,
    user_message: str,
    stop_event: Optional[Event] = None,
) -> str:
    _raise_if_cancelled(stop_event)

    if stop_event is None:
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        return response["message"]["content"]

    kill_thread = None
    if stop_event is not None:
        from threading import Thread
        kill_thread = Thread(target=_kill_ollama_on_stop, args=(stop_event,), daemon=True)
        kill_thread.start()

    try:
        streamed_response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            stream=True,
        )

        chunks: list[str] = []
        last_check = time.time()

        for chunk in streamed_response:
            _raise_if_cancelled(stop_event)

            now = time.time()
            if now - last_check > 0.1:
                _raise_if_cancelled(stop_event)
                last_check = now

            content = chunk.get("message", {}).get("content", "")
            if content:
                chunks.append(content)

        return "".join(chunks)

    except RuntimeError as e:
        if "cancelled" in str(e).lower() or "stopped by user" in str(e).lower():
            time.sleep(0.5)
            raise
        raise



def build_target_json(
    model_name: str,
    natural_description: str,
    stop_event: Optional[Event] = None,
) -> dict:
    json_builder_prompt = load_text_file(JSON_BUILDER_PROMPT_PATH)

    user_message = (
        "Convert the following natural language description into the required JSON schema.\n\n"
        "Return only valid JSON. Do not include markdown fences, comments, or explanations.\n"
        "Do not rename keys. Do not omit required keys.\n\n"
        f"Description:\n{natural_description}"
    )

    raw_output = call_ollama(
        model_name,
        json_builder_prompt,
        user_message,
        stop_event=stop_event,
    )

    target_system = extract_json_from_model_output(raw_output)

    validate_target_json(target_system)

    return target_system


def build_risk_analysis_message(target_system: dict) -> str:
    target_json = json.dumps(target_system, indent=2, ensure_ascii=False)

    return (
        "Analyze the following LLM-based chatbot system.\n\n"
        "Target system description:\n\n"
        f"{target_json}\n\n"
        "Generate the defensive risk report following the required markdown format."
    )


def generate_risk_report(
    model_name: str,
    target_system: dict,
    stop_event: Optional[Event] = None,
) -> str:
    virtual_hacker_prompt = load_text_file(VIRTUAL_HACKER_PROMPT_PATH)
    user_message = build_risk_analysis_message(target_system)

    return call_ollama(
        model_name,
        virtual_hacker_prompt,
        user_message,
        stop_event=stop_event,
    )


def save_outputs(model_name: str, target_system: dict, risk_report: str) -> dict:
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    model_file_name = safe_filename(model_name)

    generated_target_path = OUTPUT_DIR / f"generated_target_{model_file_name}_{timestamp}.json"
    report_path = OUTPUT_DIR / f"risk_report_{model_file_name}_{timestamp}.md"

    generated_target_path.write_text(
        json.dumps(target_system, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    final_report = f"""<!--
Generated by Virtual Hacker
Model: {model_name}
Timestamp: {timestamp}
Input mode: natural language -> generated JSON -> validated JSON -> risk report
-->

{risk_report}
"""

    report_path.write_text(final_report, encoding="utf-8")

    return {
        "json_path": str(generated_target_path),
        "report_path": str(report_path),
        "timestamp": timestamp,
    }



def run_virtual_hacker_analysis(
    natural_description: str,
    model_name: str = "qwen2.5:7b",
    stop_event: Optional[Event] = None,
) -> dict:
    natural_description = natural_description.strip()

    if not natural_description:
        return {
            "ok": False,
            "error": "No description provided.",
        }

    try:
        _raise_if_cancelled(stop_event)
        target_system = build_target_json(
            model_name,
            natural_description,
            stop_event=stop_event,
        )
        _raise_if_cancelled(stop_event)
        risk_report = generate_risk_report(
            model_name,
            target_system,
            stop_event=stop_event,
        )
        _raise_if_cancelled(stop_event)
        output_paths = save_outputs(model_name, target_system, risk_report)

        return {
            "ok": True,
            "target_system": target_system,
            "risk_report": risk_report,
            "json_path": output_paths["json_path"],
            "report_path": output_paths["report_path"],
            "timestamp": output_paths["timestamp"],
        }

    except Exception as e:
        if stop_event is not None and stop_event.is_set():
            return {
                "ok": False,
                "cancelled": True,
                "error": "Analysis stopped by user.",
            }

        return {
            "ok": False,
            "error": str(e),
        }



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Virtual Hacker interactive pipeline"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5:7b",
        help="Ollama model name, for example qwen2.5:7b or mistral:7b",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_name = args.model

    print("Virtual Hacker - Natural Language Pipeline")
    print(f"Using model: {model_name}")
    print("\nDescribe your LLM-based chatbot system.")
    print("When you finish, press ENTER twice.\n")

    lines = []

    while True:
        line = input("> ")
        if line.strip() == "":
            break
        lines.append(line)

    natural_description = "\n".join(lines).strip()

    if not natural_description:
        print("No description provided.")
        return

    print("\nRunning Virtual Hacker analysis...")

    result = run_virtual_hacker_analysis(
        natural_description=natural_description,
        model_name=model_name,
    )

    if not result["ok"]:
        print("\nError:")
        print(result["error"])
        return

    print("\nDone.")
    print(f"Generated target JSON saved in: {result['json_path']}")
    print(f"Risk report saved in: {result['report_path']}")


if __name__ == "__main__":
    main()
