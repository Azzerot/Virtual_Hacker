import argparse
import json
from pathlib import Path
from datetime import datetime
from threading import Event
import time
import subprocess
from typing import Optional, Any

import ollama
from jsonschema import validate, ValidationError


BASE_DIR = Path(__file__).resolve().parent

JSON_BUILDER_PROMPT_PATH = BASE_DIR / "prompts" / "json_builder_prompt.txt"
VIRTUAL_HACKER_PROMPT_PATH = BASE_DIR / "prompts" / "virtual_hacker_prompt.txt"
RISK_NORMALIZER_PROMPT_PATH = BASE_DIR / "prompts" / "risk_normalizer_prompt.txt"
MITIGATION_ENGINE_PROMPT_PATH = BASE_DIR / "prompts" / "mitigation_engine_prompt.txt"
REPORT_VALIDATOR_PROMPT_PATH = BASE_DIR / "prompts" / "report_validator_prompt.txt"

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
        "system_name": {"type": "string", "minLength": 1},
        "system_type": {"type": "string", "minLength": 1},
        "description": {"type": "string", "minLength": 1},
        "reference_architecture": {"type": "string", "minLength": 1},
        "users": {"type": "array", "items": {"type": "string"}},
        "components": {"type": "array", "items": {"type": "string"}},
        "data_handled": {"type": "array", "items": {"type": "string"}},
        "security_assumptions": {"type": "array", "items": {"type": "string"}},
        "attacker_model": {
            "type": "object",
            "required": [
                "attacker_type",
                "access_level",
                "capabilities",
                "limitations",
            ],
            "properties": {
                "attacker_type": {"type": "string", "minLength": 1},
                "access_level": {"type": "string", "minLength": 1},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
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


ALLOWED_ANALYSIS_SCOPE = {
    "prompt injection",
    "privacy leakage",
    "hallucination",
    "resource exhaustion",
    "tool misuse",
    "unauthorized access",
    "information disclosure",
}


TARGET_SYSTEM_KEYS = {
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
}


ATTACKER_MODEL_KEYS = {
    "attacker_type",
    "access_level",
    "capabilities",
    "limitations",
}


def is_unknown(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() == "unknown"


def is_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 0


def clean_string(value: Any, default: str = "unknown") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()

    return default


def clean_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    cleaned_items: list[str] = []

    for item in value:
        if isinstance(item, str) and item.strip():
            cleaned_items.append(item.strip())

    return cleaned_items


def normalize_target_json(target_system: dict) -> dict:
    if not isinstance(target_system, dict):
        target_system = {}

    normalized = {
        key: value
        for key, value in target_system.items()
        if key in TARGET_SYSTEM_KEYS
    }

    normalized["system_name"] = clean_string(
        normalized.get("system_name"),
        default="unknown",
    )

    normalized["system_type"] = "LLM-based chatbot"

    normalized["description"] = clean_string(
        normalized.get("description"),
        default="unknown",
    )

    normalized["reference_architecture"] = clean_string(
        normalized.get("reference_architecture"),
        default="unknown",
    )

    normalized["users"] = clean_string_list(normalized.get("users"))
    normalized["components"] = clean_string_list(normalized.get("components"))
    normalized["data_handled"] = clean_string_list(normalized.get("data_handled"))
    normalized["security_assumptions"] = clean_string_list(
        normalized.get("security_assumptions")
    )

    analysis_scope = clean_string_list(normalized.get("analysis_scope"))
    normalized["analysis_scope"] = [
        item for item in analysis_scope if item in ALLOWED_ANALYSIS_SCOPE
    ]

    attacker_model = normalized.get("attacker_model")

    if not isinstance(attacker_model, dict):
        attacker_model = {}

    attacker_model = {
        key: value
        for key, value in attacker_model.items()
        if key in ATTACKER_MODEL_KEYS
    }

    normalized["attacker_model"] = {
        "attacker_type": clean_string(
            attacker_model.get("attacker_type"),
            default="unknown",
        ),
        "access_level": clean_string(
            attacker_model.get("access_level"),
            default="unknown",
        ),
        "capabilities": clean_string_list(attacker_model.get("capabilities")),
        "limitations": clean_string_list(attacker_model.get("limitations")),
    }

    return normalized


def enrich_target_json_from_input(
    target_system: dict,
    natural_description: str,
) -> dict:
    enriched = dict(target_system)
    cleaned_input = natural_description.strip()

    if is_unknown(enriched.get("description")) and len(cleaned_input) >= 40:
        enriched["description"] = cleaned_input[:700]

    if (
        is_unknown(enriched.get("reference_architecture"))
        and enriched.get("components")
    ):
        components_summary = ", ".join(enriched["components"])
        enriched["reference_architecture"] = (
            f"LLM-based chatbot architecture including: {components_summary}."
        )

    return enriched


def check_json_completeness(target_system: dict) -> dict:
    missing_fields = []
    warnings = []
    suggested_questions = []

    if is_unknown(target_system.get("system_name")):
        warnings.append("System name is unknown.")
        suggested_questions.append("What is the name of the chatbot system?")

    if is_unknown(target_system.get("description")):
        missing_fields.append("description")
        warnings.append("Description is missing or unknown.")
        suggested_questions.append("Can you briefly describe what the chatbot does?")

    if is_unknown(target_system.get("reference_architecture")):
        missing_fields.append("reference_architecture")
        warnings.append("Reference architecture is unknown.")
        suggested_questions.append(
            "Can you describe the chatbot architecture, including model, UI, backend, APIs, RAG, databases, or external tools?"
        )

    if is_empty_list(target_system.get("users")):
        missing_fields.append("users")
        warnings.append("No user roles are defined.")
        suggested_questions.append(
            "Who uses the chatbot? For example: customers, employees, admins, support agents, developers."
        )

    if is_empty_list(target_system.get("components")):
        missing_fields.append("components")
        warnings.append("No technical components are defined.")
        suggested_questions.append(
            "Which technical components are part of the chatbot system? For example: web UI, LLM API, backend, database, RAG, vector store, tools, plugins, authentication system."
        )

    if is_empty_list(target_system.get("data_handled")):
        missing_fields.append("data_handled")
        warnings.append("No handled data types are defined.")
        suggested_questions.append(
            "What types of data does the chatbot process, store, retrieve, or display?"
        )

    if is_empty_list(target_system.get("security_assumptions")):
        warnings.append("No security assumptions or expected protections are defined.")
        suggested_questions.append(
            "Are there any security constraints or protections? For example: no disclosure of internal prompts, no access to private user data, authentication required, logging enabled, output filtering."
        )

    attacker_model = target_system.get("attacker_model", {})

    if is_unknown(attacker_model.get("attacker_type")):
        missing_fields.append("attacker_model.attacker_type")
        warnings.append("Attacker type is unknown.")
        suggested_questions.append(
            "What type of attacker should be considered? For example: anonymous user, authenticated user, malicious customer, insider, external attacker."
        )

    if is_unknown(attacker_model.get("access_level")):
        missing_fields.append("attacker_model.access_level")
        warnings.append("Attacker access level is unknown.")
        suggested_questions.append(
            "What access level does the attacker have? For example: public chat access, authenticated account, admin access, API access."
        )

    if is_empty_list(attacker_model.get("capabilities")):
        missing_fields.append("attacker_model.capabilities")
        warnings.append("Attacker capabilities are not defined.")
        suggested_questions.append(
            "What can the attacker do? For example: send messages, upload files, call APIs, view responses, create accounts, access shared conversations."
        )

    if is_empty_list(attacker_model.get("limitations")):
        warnings.append("Attacker limitations are not defined.")
        suggested_questions.append(
            "What can the attacker not do? For example: no admin access, no database access, no source code access, no direct model access."
        )

    analysis_scope = target_system.get("analysis_scope", [])

    if is_empty_list(analysis_scope):
        missing_fields.append("analysis_scope")
        warnings.append("Analysis scope is empty.")
        suggested_questions.append(
            "Which risk categories should be prioritized? Choose from: prompt injection, privacy leakage, hallucination, resource exhaustion, tool misuse, unauthorized access, information disclosure."
        )
    else:
        invalid_scope_values = [
            item for item in analysis_scope if item not in ALLOWED_ANALYSIS_SCOPE
        ]

        if invalid_scope_values:
            warnings.append(
                f"Invalid analysis_scope values found: {invalid_scope_values}."
            )
            suggested_questions.append(
                "Please use only the allowed analysis_scope values: prompt injection, privacy leakage, hallucination, resource exhaustion, tool misuse, unauthorized access, information disclosure."
            )

    critical_missing = {
        "description",
        "reference_architecture",
        "components",
        "data_handled",
        "attacker_model.access_level",
        "attacker_model.capabilities",
        "analysis_scope",
    }

    missing_critical_count = len(set(missing_fields).intersection(critical_missing))

    if missing_critical_count >= 4:
        quality_status = "insufficient"
    elif missing_critical_count >= 1 or len(warnings) >= 3:
        quality_status = "partial"
    else:
        quality_status = "complete"

    unique_questions = []

    for question in suggested_questions:
        if question not in unique_questions:
            unique_questions.append(question)

    return {
        "quality_status": quality_status,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "suggested_questions": unique_questions,
    }


def should_block_risk_report(quality_result: dict) -> bool:
    blocking_fields = {
        "components",
        "data_handled",
        "attacker_model.attacker_type",
        "attacker_model.access_level",
        "attacker_model.capabilities",
        "analysis_scope",
    }

    missing_fields = set(quality_result.get("missing_fields", []))

    return (
        quality_result.get("quality_status") == "insufficient"
        or bool(missing_fields.intersection(blocking_fields))
    )


def build_quality_markdown(quality_result: Optional[dict]) -> str:
    if not quality_result:
        return ""

    quality_markdown = "## JSON Completeness Check\n\n"
    quality_markdown += f"**Status:** `{quality_result.get('quality_status', 'unknown')}`\n\n"

    missing_fields = quality_result.get("missing_fields", [])
    warnings = quality_result.get("warnings", [])
    suggested_questions = quality_result.get("suggested_questions", [])

    if missing_fields:
        quality_markdown += "### Missing Fields\n\n"
        for field in missing_fields:
            quality_markdown += f"- {field}\n"

    if warnings:
        quality_markdown += "\n### Warnings\n\n"
        for warning in warnings:
            quality_markdown += f"- {warning}\n"

    if suggested_questions:
        quality_markdown += "\n### Suggested Questions\n\n"
        for question in suggested_questions:
            quality_markdown += f"- {question}\n"

    return quality_markdown


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding="utf-8")


def safe_filename(text: str) -> str:
    return (
        text.replace(":", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


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

    except json.JSONDecodeError:
        start = cleaned_output.find("{")
        end = cleaned_output.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "The model did not return valid JSON and no JSON object could be extracted.\n\n"
                f"Raw model output:\n{raw_output}"
            )

        possible_json = cleaned_output[start : end + 1]

        try:
            parsed_json = json.loads(possible_json)

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
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        return response["message"]["content"]

    from threading import Thread

    kill_thread = Thread(
        target=_kill_ollama_on_stop,
        args=(stop_event,),
        daemon=True,
    )
    kill_thread.start()

    try:
        streamed_response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
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
        "Do not rename keys. Do not omit required keys.\n"
        "Use exact allowed values for analysis_scope.\n"
        "Extract description, reference_architecture, users, components, data_handled, "
        "security_assumptions, attacker capabilities, and attacker limitations as precisely as possible.\n"
        "If information is missing, keep the required key and use 'unknown' for string fields or [] for list fields.\n"
        "Do not invent facts that are not present in the description.\n\n"
        f"Description:\n{natural_description}"
    )

    raw_output = call_ollama(
        model_name,
        json_builder_prompt,
        user_message,
        stop_event=stop_event,
    )

    target_system = extract_json_from_model_output(raw_output)

    target_system = normalize_target_json(target_system)

    target_system = enrich_target_json_from_input(
        target_system=target_system,
        natural_description=natural_description,
    )

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


def build_risk_normalization_message(
    target_system: dict,
    quality_result: dict,
    risk_report: str,
) -> str:
    target_json = json.dumps(target_system, indent=2, ensure_ascii=False)
    quality_json = json.dumps(quality_result, indent=2, ensure_ascii=False)

    return (
        "Normalize the following defensive LLM security risk report.\n\n"
        "Generated target JSON:\n"
        f"{target_json}\n\n"
        "JSON quality result:\n"
        f"{quality_json}\n\n"
        "Generated risk report:\n"
        f"{risk_report}\n\n"
        "Return only the normalized markdown report."
    )


def normalize_risk_report(
    model_name: str,
    target_system: dict,
    quality_result: dict,
    risk_report: str,
    stop_event: Optional[Event] = None,
) -> str:
    risk_normalizer_prompt = load_text_file(RISK_NORMALIZER_PROMPT_PATH)

    user_message = build_risk_normalization_message(
        target_system=target_system,
        quality_result=quality_result,
        risk_report=risk_report,
    )

    return call_ollama(
        model_name,
        risk_normalizer_prompt,
        user_message,
        stop_event=stop_event,
    )


def build_mitigation_enhancement_message(
    target_system: dict,
    quality_result: dict,
    risk_report: str,
) -> str:
    target_json = json.dumps(target_system, indent=2, ensure_ascii=False)
    quality_json = json.dumps(quality_result, indent=2, ensure_ascii=False)

    return (
        "Enhance only the Defensive Mitigations sections of the following normalized report.\n\n"
        "Generated target JSON:\n"
        f"{target_json}\n\n"
        "JSON quality result:\n"
        f"{quality_json}\n\n"
        "Normalized risk report:\n"
        f"{risk_report}\n\n"
        "Return only the enhanced markdown report."
    )


def enhance_mitigations(
    model_name: str,
    target_system: dict,
    quality_result: dict,
    risk_report: str,
    stop_event: Optional[Event] = None,
) -> str:
    mitigation_engine_prompt = load_text_file(MITIGATION_ENGINE_PROMPT_PATH)

    user_message = build_mitigation_enhancement_message(
        target_system=target_system,
        quality_result=quality_result,
        risk_report=risk_report,
    )

    return call_ollama(
        model_name,
        mitigation_engine_prompt,
        user_message,
        stop_event=stop_event,
    )


def validate_risk_report(
    model_name: str,
    natural_description: str,
    target_system: dict,
    quality_result: dict,
    risk_report: str,
    stop_event: Optional[Event] = None,
) -> dict:
    report_validator_prompt = load_text_file(REPORT_VALIDATOR_PROMPT_PATH)

    target_json = json.dumps(target_system, indent=2, ensure_ascii=False)
    quality_json = json.dumps(quality_result, indent=2, ensure_ascii=False)

    user_message = (
        "Validate whether the generated risk report is coherent with the original input, "
        "the generated target JSON, and the JSON quality result.\n\n"
        "Original user input:\n"
        f"{natural_description}\n\n"
        "Generated target JSON:\n"
        f"{target_json}\n\n"
        "JSON quality result:\n"
        f"{quality_json}\n\n"
        "Generated risk report:\n"
        f"{risk_report}\n\n"
        "Return only valid JSON."
    )

    raw_output = call_ollama(
        model_name,
        report_validator_prompt,
        user_message,
        stop_event=stop_event,
    )

    return extract_json_from_model_output(raw_output)


def save_outputs(
    model_name: str,
    target_system: dict,
    risk_report: str,
    quality_result: Optional[dict] = None,
    report_validation_result: Optional[dict] = None,
    raw_risk_report: Optional[str] = None,
    normalized_risk_report: Optional[str] = None,
) -> dict:
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    model_file_name = safe_filename(model_name)

    generated_target_path = OUTPUT_DIR / f"generated_target_{model_file_name}_{timestamp}.json"
    report_path = OUTPUT_DIR / f"risk_report_{model_file_name}_{timestamp}.md"
    quality_path = OUTPUT_DIR / f"quality_check_{model_file_name}_{timestamp}.json"
    report_validation_path = OUTPUT_DIR / f"report_validation_{model_file_name}_{timestamp}.json"
    raw_report_path = OUTPUT_DIR / f"raw_risk_report_{model_file_name}_{timestamp}.md"
    normalized_report_path = OUTPUT_DIR / f"normalized_risk_report_{model_file_name}_{timestamp}.md"

    generated_target_path.write_text(
        json.dumps(target_system, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if quality_result is not None:
        quality_path.write_text(
            json.dumps(quality_result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if report_validation_result is not None:
        report_validation_path.write_text(
            json.dumps(report_validation_result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if raw_risk_report is not None:
        raw_report_path.write_text(raw_risk_report, encoding="utf-8")

    if normalized_risk_report is not None:
        normalized_report_path.write_text(normalized_risk_report, encoding="utf-8")

    quality_markdown = build_quality_markdown(quality_result)

    final_report = f"""<!--
Generated by Virtual Hacker
Model: {model_name}
Timestamp: {timestamp}
Input mode: natural language -> generated JSON -> normalized JSON -> enriched JSON -> validated JSON -> completeness check -> risk report -> risk normalization -> mitigation enhancement -> report validation
-->

{quality_markdown}

{risk_report}
"""

    report_path.write_text(final_report, encoding="utf-8")

    result = {
        "json_path": str(generated_target_path),
        "report_path": str(report_path),
        "timestamp": timestamp,
    }

    if quality_result is not None:
        result["quality_path"] = str(quality_path)

    if report_validation_result is not None:
        result["report_validation_path"] = str(report_validation_path)

    if raw_risk_report is not None:
        result["raw_report_path"] = str(raw_report_path)

    if normalized_risk_report is not None:
        result["normalized_report_path"] = str(normalized_report_path)

    return result


def build_insufficient_error_message(quality_result: dict) -> str:
    questions = quality_result.get("suggested_questions", [])

    if not questions:
        return (
            "The generated JSON is valid, but not complete enough for a reliable risk analysis. "
            "Please provide more details and run the analysis again."
        )

    question_lines = "\n".join(f"- {question}" for question in questions)

    return (
        "The generated JSON is valid, but not complete enough for a reliable risk analysis. "
        "Please answer the suggested questions below and run the analysis again.\n\n"
        f"{question_lines}"
    )


def run_virtual_hacker_analysis(
    natural_description: str,
    model_name: str = "qwen2.5:32b",
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

        quality_result = check_json_completeness(target_system)

        if should_block_risk_report(quality_result):
            return {
                "ok": False,
                "error": build_insufficient_error_message(quality_result),
                "target_system": target_system,
                "quality_result": quality_result,
            }

        raw_risk_report = generate_risk_report(
            model_name,
            target_system,
            stop_event=stop_event,
        )

        _raise_if_cancelled(stop_event)

        normalized_risk_report = normalize_risk_report(
            model_name=model_name,
            target_system=target_system,
            quality_result=quality_result,
            risk_report=raw_risk_report,
            stop_event=stop_event,
        )

        _raise_if_cancelled(stop_event)

        enhanced_risk_report = enhance_mitigations(
            model_name=model_name,
            target_system=target_system,
            quality_result=quality_result,
            risk_report=normalized_risk_report,
            stop_event=stop_event,
        )

        _raise_if_cancelled(stop_event)

        report_validation_result = validate_risk_report(
            model_name=model_name,
            natural_description=natural_description,
            target_system=target_system,
            quality_result=quality_result,
            risk_report=enhanced_risk_report,
            stop_event=stop_event,
        )

        _raise_if_cancelled(stop_event)

        output_paths = save_outputs(
            model_name=model_name,
            target_system=target_system,
            risk_report=enhanced_risk_report,
            quality_result=quality_result,
            report_validation_result=report_validation_result,
            raw_risk_report=raw_risk_report,
            normalized_risk_report=normalized_risk_report,
        )

        return {
            "ok": True,
            "target_system": target_system,
            "quality_result": quality_result,
            "report_validation_result": report_validation_result,
            "risk_report": enhanced_risk_report,
            "raw_risk_report": raw_risk_report,
            "normalized_risk_report": normalized_risk_report,
            "json_path": output_paths["json_path"],
            "quality_path": output_paths.get("quality_path"),
            "report_validation_path": output_paths.get("report_validation_path"),
            "raw_report_path": output_paths.get("raw_report_path"),
            "normalized_report_path": output_paths.get("normalized_report_path"),
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
        default="qwen2.5:32b",
        help="Ollama model name, for example qwen2.5:32b or mistral:7b",
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

        if "quality_result" in result:
            print("\nJSON Completeness Check:")
            print(json.dumps(result["quality_result"], indent=2, ensure_ascii=False))

        if "target_system" in result:
            print("\nGenerated JSON:")
            print(json.dumps(result["target_system"], indent=2, ensure_ascii=False))

        return

    print("\nDone.")
    print(f"Generated target JSON saved in: {result['json_path']}")

    if result.get("quality_path"):
        print(f"Quality check saved in: {result['quality_path']}")

    if result.get("raw_report_path"):
        print(f"Raw risk report saved in: {result['raw_report_path']}")

    if result.get("normalized_report_path"):
        print(f"Normalized risk report saved in: {result['normalized_report_path']}")

    if result.get("report_validation_path"):
        print(f"Report validation saved in: {result['report_validation_path']}")

    print(f"Final enhanced risk report saved in: {result['report_path']}")


if __name__ == "__main__":
    main()